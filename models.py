from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for saved properties (many-to-many)
saved_properties = db.Table('saved_properties',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('property_id', db.Integer, db.ForeignKey('property.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'

    # Verification fields
    verification_status = db.Column(db.String(20), default='unverified')  # 'unverified', 'pending', 'verified', 'rejected'
    id_type = db.Column(db.String(50))
    id_number = db.Column(db.String(50))
    id_expiry = db.Column(db.String(50))
    id_front_url = db.Column(db.String(500))
    id_back_url = db.Column(db.String(500))
    full_name_on_doc = db.Column(db.String(100))
    verification_submitted_at = db.Column(db.DateTime)

    # Relationships
    properties = db.relationship('Property', backref='owner', lazy=True)
    saved_list = db.relationship('Property', secondary=saved_properties, backref=db.backref('saved_by', lazy='dynamic'))
    saved_searches = db.relationship('SavedSearch', backref='user', lazy=True)
    alerts = db.relationship('SearchAlert', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    listing_type = db.Column(db.String(50), nullable=False)  # 'buy' or 'rent'
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    area = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(50))
    city = db.Column(db.String(100))
    year_built = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    tags = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        # ✅ تم التصحيح: جلب الـ owner مرة واحدة بدل استدعاءين منفصلين
        owner = db.session.get(User, self.owner_id) if self.owner_id else None
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'location': [self.lat, self.lng],
            'listing_type': self.listing_type,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'area': self.area,
            'imageUrl': self.image_url,
            'image_url': self.image_url,
            # ✅ تم التصحيح: بناء الـ URL الصح للصور بدل إرجاع اسم الملف فقط
            'images': [f"static/uploads/{img.image_url}" for img in self.images],
            'description': self.description,
            'contactEmail': self.contact_email or (owner.email if owner else None),
            'contactPhone': self.contact_phone,
            'city': self.city,
            'yearBuilt': self.year_built,
            'lat': self.lat,
            'lng': self.lng,
            'status': self.status,
            'tags': self.tags or []
        }


class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)


class SavedSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    filters = db.Column(db.JSON)  # Store search filters as JSON
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class SearchAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    criteria = db.Column(db.Text)
    frequency = db.Column(db.String(20), default='instant')  # 'instant', 'daily', 'weekly'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())