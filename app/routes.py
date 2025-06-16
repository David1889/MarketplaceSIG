from flask import Blueprint, request, jsonify
from app import db
from app.models import Shop, Product, User
from geoalchemy2.functions import ST_DWithin
from sqlalchemy import func
from geopy.geocoders import Nominatim

routes = Blueprint('routes', __name__)

@routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email ya registrado'}), 400
    user = User(
        name=data.get('name'),
        email=data.get('email'),
        password=data.get('password'),
        type=data.get('type')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Usuario registrado', 'user_id': user.id})

@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email'), password=data.get('password')).first()
    if not user:
        return jsonify({'error': 'Credenciales incorrectas'}), 401
    return jsonify({'message': 'Login exitoso', 'user_id': user.id, 'type': user.type})

@routes.route('/me', methods=['GET'])
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

@routes.route('/shops', methods=['POST'])
def create_shop():
    data = request.json
    address = data.get('address')
    if not address:
        return jsonify({"error": "Se requiere una dirección"}), 400

    geolocator = Nominatim(user_agent="marketplace_sig_app")
    location = geolocator.geocode(address)
    if not location:
        return jsonify({"error": "Dirección no encontrada"}), 400

    # Crear objeto Shop con coordenadas en formato WKT POINT(long lat)
    point_wkt = f'POINT({location.longitude} {location.latitude})'
    shop = Shop(
        name=data['name'],
        coordinates=point_wkt,
        user_id=data['user_id']
    )
    db.session.add(shop)
    db.session.commit()

    response = {
        "id": shop.id,
        "name": shop.name,
        "coordinates": {
            "lat": location.latitude,
            "lng": location.longitude
        },
        "user_id": shop.user_id
    }
    return jsonify(response), 201

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
            'user_id': shop.user_id
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
        'user_id': shop.user_id
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