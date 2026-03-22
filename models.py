from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    death_date = db.Column(db.Date, nullable=True)
    is_living = db.Column(db.Boolean, default=False)
    birth_place = db.Column(db.String(100), nullable=True)
    death_place = db.Column(db.String(100), nullable=True)
    nationality = db.Column(db.String(100), nullable=True)
    art_movement = db.Column(db.String(100), nullable=True)
    primary_medium = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    artworks = db.relationship('Artwork', backref='artist', lazy='dynamic')


class Artwork(db.Model):
    __tablename__ = 'artworks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=True)
    medium = db.Column(db.String(100), nullable=True)
    art_movement = db.Column(db.String(100), nullable=True)
    subject = db.Column(db.String(100), nullable=True)
    creation_date = db.Column(db.Date, nullable=True)
    dimension_H = db.Column(db.Numeric(10, 2), nullable=True)
    dimension_W = db.Column(db.Numeric(10, 2), nullable=True)
    dimension_D = db.Column(db.Numeric(10, 2), nullable=True)
    dimension_unit = db.Column(db.String(20), default='inches')
    weight = db.Column(db.Numeric(10, 2), nullable=True)
    weight_unit = db.Column(db.String(20), default='lbs')
    estimated_value = db.Column(db.Numeric(12, 2), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    is_signed = db.Column(db.Boolean, default=False)
    signature_location = db.Column(db.String(100), nullable=True)
    ai_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    collections = db.relationship('Collection', backref='artwork', lazy='dynamic')


class Museum(db.Model):
    __tablename__ = 'museums'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    museum_type = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state_province = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=True)
    established_date = db.Column(db.Date, nullable=True)
    website = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    annual_visitors = db.Column(db.Integer, nullable=True)
    admission_fee = db.Column(db.Numeric(10, 2), nullable=True)
    ai_collection_description = db.Column(db.Text, nullable=True)

    collections = db.relationship('Collection', backref='museum', lazy='dynamic')


class Collection(db.Model):
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    museum_id = db.Column(db.Integer, db.ForeignKey('museums.id'), nullable=False)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artworks.id'), nullable=False)
    accession_number = db.Column(db.String(50), nullable=True)
    acquisition_date = db.Column(db.Date, nullable=True)
    acquisition_method = db.Column(db.String(50), nullable=False)
    acquisition_cost = db.Column(db.Numeric(12, 2), nullable=True)
    acquisition_details = db.Column(db.Text, nullable=True)
    donor_name = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(50), default='Active')
    gallery_location = db.Column(db.String(100), nullable=True)
    on_display = db.Column(db.Boolean, default=False)
    current_value = db.Column(db.Numeric(12, 2), nullable=True)
