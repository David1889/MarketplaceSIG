from flask import Blueprint, request, jsonify
from app import db
from app.models import Shop, Product, User
from geoalchemy2.functions import ST_DWithin, ST_AsText, ST_GeographyFromText
from sqlalchemy import func, select
from geopy.geocoders import Nominatim
from app.mailer import send_email
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from sqlalchemy.exc import IntegrityError
import logging

routes = Blueprint('routes', __name__)

@routes.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    user_type = data.get('type')  # 'client', 'owner', etc.

    if not all([email, password, name, user_type]):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    user = User(
        email=email,
        password=password,
        name=name,
        type=user_type
    )

    if user_type == 'client':
        address = data.get('address')
        radius = data.get('radius', 5000)  
        if not address:
            return jsonify({"error": "El cliente debe incluir un campo 'address'"}), 400

        geolocator = Nominatim(user_agent="marketplace_sig_app")
        try:
            location = geolocator.geocode(address, timeout=10)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            return jsonify({"error": "Error de geocodificación", "detalle": str(e)}), 503

        if not location:
            return jsonify({"error": "Dirección no encontrada"}), 400

        user.coordinates = f'POINT({location.longitude} {location.latitude})'
        user.radius = radius

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "El correo ya está registrado"}), 400

    return jsonify({
        "message": "Usuario registrado correctamente",
        "user_id": user.id
    }), 201

@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email'), password=data.get('password')).first()
    if not user:
        return jsonify({'error': 'Credenciales incorrectas'}), 401
    return jsonify({'message': 'Login exitoso', 'user_id': user.id, 'type': user.type})

@routes.route('/profile', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'type': user.type,
        'coordinates': str(user.coordinates),
        'radius': user.radius
    })

@routes.route('/users', methods=['GET'])
def list_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "password": user.password,  # No deberías enviar la contraseña en una respuesta
            "email": user.email,
            "type": user.type,
            "coordinates": str(user.coordinates) if user.coordinates else None,
            "radius": user.radius
        })
    return jsonify(result)

@routes.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json()

    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = data['password']
    if 'radius' in data:
        try:
            user.radius = float(data['radius'])
        except ValueError:
            return jsonify({"error": "Radius debe ser un número"}), 400

    if 'address' in data:
        address = data['address']
        geolocator = Nominatim(user_agent="marketplace_sig_app")
        try:
            location = geolocator.geocode(address, timeout=10)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            return jsonify({"error": "Error de geocodificación", "detalle": str(e)}), 503

        if not location:
            return jsonify({"error": "Dirección no encontrada"}), 400

        user.coordinates = f'POINT({location.longitude} {location.latitude})'

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "El correo ya está registrado"}), 400

    return jsonify({
        "message": "Usuario actualizado correctamente",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "type": user.type,
            "coordinates": str(user.coordinates),
            "radius": user.radius
        }
    })


@routes.route('/shops', methods=['POST'])
def create_shop():
    data = request.json
    address = data.get('address')
    if not address:
        return jsonify({"error": "Se requiere una dirección"}), 400

    geolocator = Nominatim(user_agent="marketplace_sig_app")

    try:
        location = geolocator.geocode(address, timeout=10)
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        return jsonify({"error": "Error en el servicio de geocodificación", "detalle": str(e)}), 503

    if not location:
        return jsonify({"error": "Dirección no encontrada"}), 400

    point_wkt = f'POINT({location.longitude} {location.latitude})'
    shop = Shop(
        name=data['name'],
        coordinates=point_wkt,
        user_id=data['user_id']
    )
    db.session.add(shop)
    db.session.commit()

    return jsonify({
        "id": shop.id,
        "name": shop.name,
        "coordinates": {
            "lat": location.latitude,
            "lng": location.longitude
        },
        "user_id": shop.user_id
    }), 201

@routes.route('/shops', methods=['GET'])
def list_shops():
    #argumentos de latitud y longitud EN REVISION, tengo que ver si hay algo más óptimo para geolocalizar..
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', type=float)  #en metros.. 

    query = Shop.query

    if lat is not None and lng is not None and radius is not None:
        point_wkt = f'POINT({lng} {lat})'
        query = query.filter(
            ST_DWithin(
                Shop.coordinates,
                func.ST_GeographyFromText(f'SRID=4326;{point_wkt}'),
                radius
            )
        )
    shops = query.all()
    result = []
    for shop in shops:
        result.append({
            'id': shop.id,
            'name': shop.name,
            'coordinates': str(shop.coordinates),
            'user_id': shop.user_id,
            'status': shop.state
        })
    return jsonify(result)

@routes.route('/shops/<int:shop_id>', methods=['GET'])
def get_shop(shop_id):
    shop = Shop.query.get(shop_id)
    if not shop:
        return jsonify({'error': 'Tienda no encontrada'}), 404
    return jsonify({
        'id': shop.id,
        'name': shop.name,
        'coordinates': str(shop.coordinates),
        'user_id': shop.user_id,
        'status': shop.state

    })

@routes.route('/shops/<int:shop_id>', methods=['PUT'])
def update_shop(shop_id):
    shop = Shop.query.get(shop_id)
    if not shop:
        return jsonify({'error': 'Tienda no encontrada'}), 404
    data = request.get_json()
    if 'name' in data:
        shop.name = data['name']
    if 'lat' in data and 'lng' in data:
        shop.coordinates = f'POINT({data["lng"]} {data["lat"]})'
    if 'state' in data:
        if data['state'] not in ['pending', 'accepted', 'declined']:
            return jsonify({'error': 'Estado inválido'}), 400
        shop.state = data['state']
    db.session.commit()
    return jsonify({'message': 'Tienda actualizada'})

@routes.route('/shops/<int:shop_id>', methods=['DELETE'])
def delete_shop(shop_id):
    shop = Shop.query.get(shop_id)
    if not shop:
        return jsonify({'error': 'Tienda no encontrada'}), 404
    db.session.delete(shop)
    db.session.commit()
    return jsonify({'message': 'Tienda eliminada'})



@routes.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    shop = Shop.query.get(data.get('shop_id'))
    if not shop:
        return jsonify({'error': 'Tienda no encontrada'}), 404
    product = Product(
        name=data.get('name'),
        price=data.get('price'),
        has_discount=data.get('has_discount', False),
        discount=data.get('discount'),
        shop_id=shop.id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Producto creado', 'product_id': product.id})

@routes.route('/shops/<int:shop_id>/products', methods=['GET'])
def list_products_by_shop(shop_id):
    shop = Shop.query.get(shop_id)
    if not shop:
        return jsonify({'error': 'Tienda no encontrada'}), 404
    products = Product.query.filter_by(shop_id=shop_id).all()
    result = []
    for p in products:
        result.append({
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'has_discount': p.has_discount,
            'discount': p.discount,
            'shop_id': p.shop_id
        })
    return jsonify(result)

@routes.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'has_discount': product.has_discount,
        'discount': product.discount,
        'shop_id': product.shop_id
    })

@routes.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    data = request.get_json()
    if 'name' in data:
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'has_discount' in data:
        product.has_discount = data['has_discount']
    if 'discount' in data:
        product.discount = data['discount']
    db.session.commit()
    return jsonify({'message': 'Producto actualizado'})

@routes.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Producto no encontrado'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Producto eliminado'})

@routes.route('/send_offers', methods=['GET'])
def send_offers():
    clients = User.query.filter(
        User.type == 'client',
        User.coordinates.isnot(None),
        User.radius.isnot(None)
    ).all()
    print(clients)
    sent_count = 0
    clients_sent = []
    print(clients_sent)
    for client in clients:
        try:
            wkt = db.session.scalar(select(ST_AsText(client.coordinates)))
            if not wkt:
                logging.info(f"Cliente {client.id} sin coordenadas WKT")
                continue
            print(wkt)
            long_lat = wkt.replace('POINT(', '').replace(')', '').split()
            longitude, latitude = float(long_lat[0]), float(long_lat[1])
            logging.info(f"Cliente {client.id} coord: {longitude}, {latitude} radio: {client.radius}")
            print(longitude,latitude)
            point = func.ST_GeographyFromText(f'SRID=4326;POINT({longitude} {latitude})')
            print(point)
            nearby_shops = Shop.query.filter(
                ST_DWithin(Shop.coordinates, point, client.radius),
                Shop.state == 'accepted'
            ).all()
            print(nearby_shops)
            print(f"Cliente {client.id} encontró {len(nearby_shops)} tiendas cercanas")

            offers = []
            for shop in nearby_shops:
                discounted_products = Product.query.filter_by(shop_id=shop.id, has_discount=True).all()
                print(f"Tienda {shop.id} tiene {len(discounted_products)} productos con descuento")
                for product in discounted_products:
                    offers.append(f"- {product.name} (${product.price}) en {shop.name}")
            print(offers)

            if offers:
                print(client.email)
                body = f"Hola {client.name},\n\n¡Estas son las ofertas cerca tuyo!\n\n" + "\n".join(offers)
                send_email(to=client.email, subject="Ofertas cerca tuyo", body=body)
                
                sent_count += 1

                clients_sent.append({
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "coordinates": {"lat": latitude, "lng": longitude},
                    "radius": client.radius,
                    "offers": offers
                })

        except Exception as e:
            logging.error(f"Error al enviar ofertas al cliente {client.id}: {e}")

    logging.info(f"Total correos enviados: {sent_count}")
    return jsonify({
        "message": f"Correos enviados a {sent_count} clientes con ofertas.",
        "clients": clients_sent
    })