from . import db
from geoalchemy2 import Geography
from sqlalchemy.dialects.postgresql import ENUM

user_type_enum = ENUM('client', 'owner','admin', name='user_type', create_type=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable = False)
    type = db.Column(user_type_enum, nullable=False)
    coordinates = db.Column(Geography(geometry_type='POINT', srid=4326))  # longitud, latitud
    radius = db.Column(db.Float, default=5.0)

    shops = db.relationship("Shop", backref="owner", lazy=True)


class Shop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    coordinates = db.Column(Geography(geometry_type='POINT', srid=4326))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    products = db.relationship("Product", backref="shop", lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    has_discount = db.Column(db.Boolean, default=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
