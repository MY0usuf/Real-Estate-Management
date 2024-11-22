from datetime import datetime
from main import db
from sqlalchemy import Date
from flask_login import UserMixin

class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Investor(db.Model):
    __tablename__ = 'investor'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    '''    contact_number = db.Column(db.String(20), nullable=False)
    passport_number = db.Column(db.String(20), nullable=False)
    emirates_id_number = db.Column(db.String(20), nullable=False)'''
    properties = db.relationship('Property', backref='investor', lazy=True, cascade='all, delete-orphan')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('investor', lazy=True))
    document = db.Column(db.String(120), nullable=True)

class Tenant(db.Model):
    __tablename__ = 'tenant'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email_address = db.Column(db.String(20), nullable=False)
    passport_number = db.Column(db.String(20), nullable=False)
    emirates_id_number = db.Column(db.String(20), nullable=False)
    contract_start_date = db.Column(Date, nullable=False)
    contract_end_date = db.Column(Date, nullable=False)
    no_of_cheques = db.Column(db.Integer, nullable=False)
    rental_amount = db.Column(db.Integer, nullable=False)
    security_deposit = db.Column(db.Integer, nullable=False)
    property_id = db.Column(db.String, db.ForeignKey('property.id'), nullable=False)
    is_current_tenant = db.Column(db.Boolean, default=True)
    document = db.Column(db.String(120), nullable=True)

class Property(db.Model):
    __tablename__ = 'property'
    id = db.Column(db.String, primary_key=True)
    building_name = db.Column(db.String(100), nullable=False)
    unit_no = db.Column(db.String(100), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    square_feet = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    tenant = db.relationship('Tenant', backref='property', lazy=True, cascade='all, delete-orphan')
    owner_id = db.Column(db.String, db.ForeignKey('investor.id'), nullable=False)
    document = db.Column(db.String(120), nullable=True)
