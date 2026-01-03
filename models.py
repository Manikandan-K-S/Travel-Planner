"""
Payanam - Database Models
All SQLAlchemy models for the application
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import json

db = SQLAlchemy()


class User(db.Model):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    avatar_url = db.Column(db.String(500), default='')
    language_pref = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='owner', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'language_pref': self.language_pref,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Trip(db.Model):
    """Trip model for storing trip information and itinerary"""
    __tablename__ = 'trips'
    
    trip_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    trip_name = db.Column(db.String(200), nullable=False)
    trip_description = db.Column(db.Text, default='')
    trip_category = db.Column(db.String(50), default='leisure')
    cover_image = db.Column(db.String(500), default='')
    start_date = db.Column(db.String(20), nullable=False)
    end_date = db.Column(db.String(20), nullable=False)
    total_budget = db.Column(db.Float, default=0.0)
    is_public = db.Column(db.Boolean, default=False)
    share_code = db.Column(db.String(20), unique=True, default=lambda: str(uuid.uuid4())[:8])
    itinerary_json = db.Column(db.Text, default='{"stops": []}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'trip_id': self.trip_id,
            'user_id': self.user_id,
            'trip_name': self.trip_name,
            'trip_description': self.trip_description,
            'trip_category': self.trip_category,
            'cover_image': self.cover_image,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_budget': self.total_budget,
            'is_public': self.is_public,
            'share_code': self.share_code,
            'itinerary_json': self.itinerary_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_itinerary(self):
        """Parse and return the itinerary JSON"""
        try:
            return json.loads(self.itinerary_json)
        except:
            return {"stops": []}

    def set_itinerary(self, itinerary):
        """Set the itinerary from a dict"""
        self.itinerary_json = json.dumps(itinerary)


class City(db.Model):
    """City model for storing Indian cities information"""
    __tablename__ = 'cities'
    
    city_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    image_url = db.Column(db.String(500), default='')
    category = db.Column(db.String(50), default='heritage')  # heritage, beach, hill-station, pilgrimage, nature, adventure
    popular_score = db.Column(db.Integer, default=0)  # Higher = more popular
    avg_cost_per_day = db.Column(db.Float, default=2000.0)  # Average cost in INR
    best_time_to_visit = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('Activity', backref='city', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'city_id': self.city_id,
            'name': self.name,
            'state': self.state,
            'description': self.description,
            'image_url': self.image_url,
            'category': self.category,
            'popular_score': self.popular_score,
            'avg_cost_per_day': self.avg_cost_per_day,
            'best_time_to_visit': self.best_time_to_visit,
            'activity_count': len(self.activities) if self.activities else 0
        }


class Activity(db.Model):
    """Activity model for storing activities in each city"""
    __tablename__ = 'activities'
    
    activity_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    city_id = db.Column(db.String(36), db.ForeignKey('cities.city_id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    category = db.Column(db.String(50), default='sightseeing')  # sightseeing, food, shopping, adventure, relaxation, spiritual
    estimated_cost = db.Column(db.Float, default=0.0)  # Cost in INR
    duration_hours = db.Column(db.Float, default=2.0)  # Time in hours
    image_url = db.Column(db.String(500), default='')
    rating = db.Column(db.Float, default=4.0)  # 1-5 rating
    tips = db.Column(db.Text, default='')  # Travel tips
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'activity_id': self.activity_id,
            'city_id': self.city_id,
            'city_name': self.city.name if self.city else '',
            'state': self.city.state if self.city else '',
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'estimated_cost': self.estimated_cost,
            'duration_hours': self.duration_hours,
            'image_url': self.image_url,
            'rating': self.rating,
            'tips': self.tips
        }
