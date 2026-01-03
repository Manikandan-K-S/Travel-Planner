"""
Payanam - Indian Travel Itinerary Planner
A beautiful, UI-focused travel planning application for exploring India
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'payanam-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payanam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============== DATABASE MODELS ==============

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    avatar_url = db.Column(db.String(500), default='')
    language_pref = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
        try:
            return json.loads(self.itinerary_json)
        except:
            return {"stops": []}

    def set_itinerary(self, itinerary):
        self.itinerary_json = json.dumps(itinerary)


# ============== ROUTES ==============

# Landing Page
@app.route('/')
def index():
    return render_template('index.html')


# Auth Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            session['user_id'] = user.user_id
            session['user_name'] = user.name
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='User not found. Please sign up.')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('signup.html', error='Email already exists. Please login.')
        
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.user_id
        session['user_name'] = user.name
        return redirect(url_for('dashboard'))
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    trips = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.created_at.desc()).all()
    return render_template('dashboard.html', user=user, trips=trips)


# Trip Routes
@app.route('/trip/create', methods=['GET', 'POST'])
def create_trip():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        trip = Trip(
            user_id=session['user_id'],
            trip_name=request.form.get('trip_name'),
            trip_description=request.form.get('trip_description', ''),
            trip_category=request.form.get('trip_category', 'leisure'),
            start_date=request.form.get('start_date'),
            end_date=request.form.get('end_date'),
            cover_image=request.form.get('cover_image', '')
        )
        db.session.add(trip)
        db.session.commit()
        return redirect(url_for('itinerary_builder', trip_id=trip.trip_id))
    
    return render_template('create_trip.html')


@app.route('/trips')
def my_trips():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    trips = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.created_at.desc()).all()
    return render_template('my_trips.html', trips=trips)


@app.route('/trip/<trip_id>')
def view_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session.get('user_id') and not trip.is_public:
        return redirect(url_for('login'))
    return render_template('view_trip.html', trip=trip)


@app.route('/trip/<trip_id>/edit', methods=['GET', 'POST'])
def edit_trip(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        trip.trip_name = request.form.get('trip_name')
        trip.trip_description = request.form.get('trip_description', '')
        trip.trip_category = request.form.get('trip_category', 'leisure')
        trip.start_date = request.form.get('start_date')
        trip.end_date = request.form.get('end_date')
        trip.cover_image = request.form.get('cover_image', '')
        db.session.commit()
        return redirect(url_for('view_trip', trip_id=trip_id))
    
    return render_template('edit_trip.html', trip=trip)


@app.route('/trip/<trip_id>/delete', methods=['POST'])
def delete_trip(trip_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'success': True})


# Itinerary Builder
@app.route('/trip/<trip_id>/itinerary')
def itinerary_builder(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return redirect(url_for('dashboard'))
    
    return render_template('itinerary_builder.html', trip=trip)


@app.route('/trip/<trip_id>/timeline')
def trip_timeline(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session.get('user_id') and not trip.is_public:
        return redirect(url_for('login'))
    return render_template('timeline.html', trip=trip)


@app.route('/trip/<trip_id>/budget')
def trip_budget(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return redirect(url_for('dashboard'))
    
    return render_template('budget.html', trip=trip)


# API Routes
@app.route('/api/trip/<trip_id>/itinerary', methods=['GET', 'POST'])
def api_itinerary(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    
    if request.method == 'GET':
        return jsonify(trip.get_itinerary())
    
    if request.method == 'POST':
        if 'user_id' not in session or trip.user_id != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        trip.set_itinerary(data)
        db.session.commit()
        return jsonify({'success': True})


@app.route('/api/trip/<trip_id>/budget', methods=['POST'])
def api_update_budget(trip_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    trip.total_budget = data.get('total_budget', 0)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/trip/<trip_id>/toggle-public', methods=['POST'])
def api_toggle_public(trip_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    trip.is_public = not trip.is_public
    db.session.commit()
    return jsonify({'success': True, 'is_public': trip.is_public, 'share_code': trip.share_code})


@app.route('/api/trip/<trip_id>/update', methods=['PUT'])
def api_update_trip(trip_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    trip.trip_name = data.get('trip_name', trip.trip_name)
    trip.trip_description = data.get('trip_description', trip.trip_description)
    trip.start_date = data.get('start_date', trip.start_date)
    trip.end_date = data.get('end_date', trip.end_date)
    trip.trip_category = data.get('trip_category', trip.trip_category)
    trip.total_budget = data.get('total_budget', trip.total_budget)
    trip.cover_image = data.get('cover_image', trip.cover_image)
    trip.is_public = data.get('is_public', trip.is_public)
    
    db.session.commit()
    return jsonify({'success': True, 'trip': trip.to_dict()})


@app.route('/api/trip/<trip_id>/delete', methods=['DELETE'])
def api_delete_trip(trip_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != session['user_id']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/trips')
def api_get_trips():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    limit = request.args.get('limit', type=int)
    query = Trip.query.filter_by(user_id=session['user_id']).order_by(Trip.created_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    trips = query.all()
    return jsonify({'trips': [t.to_dict() for t in trips]})


# Shared Trip View
@app.route('/shared/<share_code>')
def shared_trip(share_code):
    trip = Trip.query.filter_by(share_code=share_code, is_public=True).first_or_404()
    return render_template('shared_trip.html', trip=trip)


@app.route('/shared/<share_code>/copy', methods=['POST'])
def copy_shared_trip(share_code):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    original_trip = Trip.query.filter_by(share_code=share_code, is_public=True).first_or_404()
    
    new_trip = Trip(
        user_id=session['user_id'],
        trip_name=f"Copy of {original_trip.trip_name}",
        trip_description=original_trip.trip_description,
        trip_category=original_trip.trip_category,
        cover_image=original_trip.cover_image,
        start_date=original_trip.start_date,
        end_date=original_trip.end_date,
        total_budget=original_trip.total_budget,
        itinerary_json=original_trip.itinerary_json
    )
    db.session.add(new_trip)
    db.session.commit()
    
    return redirect(url_for('itinerary_builder', trip_id=new_trip.trip_id))


# City Search
@app.route('/cities')
def city_search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('city_search.html')


# Activity Search
@app.route('/activities')
def activity_search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('activity_search.html')


# User Profile
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.avatar_url = request.form.get('avatar_url', '')
        user.language_pref = request.form.get('language_pref', 'en')
        db.session.commit()
        session['user_name'] = user.name
        return redirect(url_for('profile'))
    
    trips = Trip.query.filter_by(user_id=session['user_id']).all()
    return render_template('profile.html', user=user, trips=trips)


@app.route('/profile/delete', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    db.session.delete(user)
    db.session.commit()
    session.clear()
    return jsonify({'success': True})


# Analytics
@app.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    trips = Trip.query.filter_by(user_id=session['user_id']).all()
    
    # Calculate analytics data
    total_trips = len(trips)
    total_budget = sum(t.total_budget for t in trips)
    
    # City statistics
    city_visits = {}
    activity_types = {}
    category_count = {}
    monthly_trips = {}
    
    for trip in trips:
        # Category count
        cat = trip.trip_category
        category_count[cat] = category_count.get(cat, 0) + 1
        
        # Monthly trips
        if trip.created_at:
            month = trip.created_at.strftime('%Y-%m')
            monthly_trips[month] = monthly_trips.get(month, 0) + 1
        
        # Itinerary analysis
        itinerary = trip.get_itinerary()
        for stop in itinerary.get('stops', []):
            city = stop.get('city_name', 'Unknown')
            city_visits[city] = city_visits.get(city, 0) + 1
            
            for day in stop.get('days', []):
                for activity in day.get('activities', []):
                    act_type = activity.get('category', 'other')
                    activity_types[act_type] = activity_types.get(act_type, 0) + 1
    
    analytics_data = {
        'total_trips': total_trips,
        'total_budget': total_budget,
        'city_visits': city_visits,
        'activity_types': activity_types,
        'category_count': category_count,
        'monthly_trips': monthly_trips
    }
    
    return render_template('analytics.html', user=user, analytics=analytics_data, trips=trips)


# API for analytics data
@app.route('/api/analytics')
def api_analytics():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    trips = Trip.query.filter_by(user_id=session['user_id']).all()
    
    # Same calculations as above
    city_visits = {}
    activity_types = {}
    category_count = {}
    budget_by_trip = []
    
    for trip in trips:
        cat = trip.trip_category
        category_count[cat] = category_count.get(cat, 0) + 1
        budget_by_trip.append({'name': trip.trip_name, 'budget': trip.total_budget})
        
        itinerary = trip.get_itinerary()
        for stop in itinerary.get('stops', []):
            city = stop.get('city_name', 'Unknown')
            city_visits[city] = city_visits.get(city, 0) + 1
            
            for day in stop.get('days', []):
                for activity in day.get('activities', []):
                    act_type = activity.get('category', 'other')
                    activity_types[act_type] = activity_types.get(act_type, 0) + 1
    
    return jsonify({
        'total_trips': len(trips),
        'total_budget': sum(t.total_budget for t in trips),
        'city_visits': city_visits,
        'activity_types': activity_types,
        'category_count': category_count,
        'budget_by_trip': budget_by_trip
    })


# Initialize Database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized!")


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
