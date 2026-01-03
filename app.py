"""
Payanam - Indian Travel Itinerary Planner
A beautiful, UI-focused travel planning application for exploring India
"""

import os
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from models import db, User, Trip, City, Activity

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'payanam-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payanam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Admin credentials from environment
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

# Initialize db with app
db.init_app(app)


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
    
    # Get popular cities and activities for dashboard
    popular_cities = City.query.order_by(City.popular_score.desc()).limit(6).all()
    popular_activities = Activity.query.order_by(Activity.rating.desc()).limit(6).all()
    
    # Convert to dicts for JSON serialization in template
    trips_data = [t.to_dict() for t in trips]
    cities_data = [c.to_dict() for c in popular_cities]
    activities_data = [a.to_dict() for a in popular_activities]
    
    return render_template('dashboard.html', user=user, trips=trips_data,
                          popular_cities=cities_data, popular_activities=activities_data)


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
    
    cities = City.query.order_by(City.popular_score.desc()).all()
    states = db.session.query(City.state).distinct().order_by(City.state).all()
    states = [s[0] for s in states]
    
    return render_template('city_search.html', cities=[c.to_dict() for c in cities], states=states)


# Activity Search
@app.route('/activities')
def activity_search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    activities = Activity.query.order_by(Activity.rating.desc()).all()
    categories = db.session.query(Activity.category).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('activity_search.html', activities=[a.to_dict() for a in activities], categories=categories)


# API: Get all cities
@app.route('/api/cities')
def api_get_cities():
    state = request.args.get('state')
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    query = City.query
    
    if state:
        query = query.filter(City.state == state)
    if category:
        query = query.filter(City.category == category)
    if search:
        query = query.filter(City.name.ilike(f'%{search}%'))
    
    cities = query.order_by(City.popular_score.desc()).all()
    return jsonify({'cities': [c.to_dict() for c in cities]})


# API: Get single city with activities
@app.route('/api/cities/<city_id>')
def api_get_city(city_id):
    city = City.query.get_or_404(city_id)
    city_data = city.to_dict()
    city_data['activities'] = [a.to_dict() for a in city.activities]
    return jsonify(city_data)


# API: Get activities for a city
@app.route('/api/cities/<city_id>/activities')
def api_get_city_activities(city_id):
    city = City.query.get_or_404(city_id)
    activities = Activity.query.filter_by(city_id=city_id).order_by(Activity.rating.desc()).all()
    return jsonify({'activities': [a.to_dict() for a in activities]})


# API: Get all activities
@app.route('/api/activities')
def api_get_activities():
    city_id = request.args.get('city_id')
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    min_cost = request.args.get('min_cost', type=float)
    max_cost = request.args.get('max_cost', type=float)
    
    query = Activity.query
    
    if city_id:
        query = query.filter(Activity.city_id == city_id)
    if category:
        query = query.filter(Activity.category == category)
    if search:
        query = query.filter(Activity.name.ilike(f'%{search}%'))
    if min_cost is not None:
        query = query.filter(Activity.estimated_cost >= min_cost)
    if max_cost is not None:
        query = query.filter(Activity.estimated_cost <= max_cost)
    
    activities = query.order_by(Activity.rating.desc()).all()
    return jsonify({'activities': [a.to_dict() for a in activities]})


# API: Get single activity
@app.route('/api/activities/<activity_id>')
def api_get_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    return jsonify(activity.to_dict())


# API: Search cities by name (for autocomplete)
@app.route('/api/cities/search')
def api_search_cities():
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify({'cities': []})
    
    cities = City.query.filter(City.name.ilike(f'%{query}%')).limit(10).all()
    return jsonify({'cities': [c.to_dict() for c in cities]})


# API: Search activities by name (for autocomplete)
@app.route('/api/activities/search')
def api_search_activities():
    query = request.args.get('q', '').lower()
    city_name = request.args.get('city', '').lower()
    
    if len(query) < 1:
        if city_name:
            city = City.query.filter(City.name.ilike(f'%{city_name}%')).first()
            if city:
                activities = Activity.query.filter_by(city_id=city.city_id).limit(20).all()
                return jsonify({'activities': [a.to_dict() for a in activities]})
        return jsonify({'activities': []})
    
    activities_query = Activity.query.filter(Activity.name.ilike(f'%{query}%'))
    
    if city_name:
        city = City.query.filter(City.name.ilike(f'%{city_name}%')).first()
        if city:
            activities_query = activities_query.filter(Activity.city_id == city.city_id)
    
    activities = activities_query.limit(10).all()
    return jsonify({'activities': [a.to_dict() for a in activities]})


# API: Get cities in frontend format (for itinerary builder)
@app.route('/api/cities/frontend-format')
def api_get_cities_frontend_format():
    """Returns cities in the format expected by the frontend JavaScript:
    { 'CityName': { state: 'State', image: 'url', activities: ['act1', 'act2'] } }
    """
    cities = City.query.order_by(City.popular_score.desc()).all()
    
    result = {}
    for city in cities:
        activities = Activity.query.filter_by(city_id=city.city_id).order_by(Activity.rating.desc()).all()
        result[city.name] = {
            'state': city.state,
            'image': city.image_url or '',
            'category': city.category,
            'activities': [a.name for a in activities]
        }
    
    return jsonify(result)


# API: Get activities for a city by name (for frontend)
@app.route('/api/cities/by-name/<city_name>/activities')
def api_get_activities_by_city_name(city_name):
    """Get activities for a city by its name (case-insensitive)"""
    city = City.query.filter(City.name.ilike(city_name)).first()
    if not city:
        return jsonify({'activities': [], 'error': 'City not found'})
    
    activities = Activity.query.filter_by(city_id=city.city_id).order_by(Activity.rating.desc()).all()
    return jsonify({
        'city': city.to_dict(),
        'activities': [a.to_dict() for a in activities],
        'activity_names': [a.name for a in activities]  # Simple list for frontend
    })


# API: Get activities in frontend format (for activity_search page)
@app.route('/api/activities/frontend-format')
def api_get_activities_frontend_format():
    """Returns activities in the format expected by the frontend JavaScript:
    Array of { name, city, state, type, duration, cost, description }
    """
    activities = Activity.query.join(City).order_by(Activity.rating.desc()).all()
    
    result = []
    for activity in activities:
        city = City.query.get(activity.city_id)
        if city:
            result.append({
                'name': activity.name,
                'city': city.name,
                'state': city.state,
                'type': activity.category or 'sightseeing',
                'duration': f"{activity.duration_hours} hours" if activity.duration_hours else '2 hours',
                'cost': int(activity.estimated_cost) if activity.estimated_cost else 0,
                'description': activity.description or f"Popular activity in {city.name}"
            })
    
    return jsonify(result)


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


@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    """API endpoint to update user profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update name
    if data.get('name'):
        user.name = data['name'].strip()[:100]  # Limit to 100 chars
        session['user_name'] = user.name
    
    # Update avatar URL if provided
    if data.get('avatar_url'):
        user.avatar_url = data['avatar_url']
    
    # Update language preference if provided
    if data.get('language_pref'):
        user.language_pref = data['language_pref']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


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
    
    return render_template('analytics.html', user=user, analytics=analytics_data, trips=[t.to_dict() for t in trips])


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


# ============== ADMIN PANEL ==============

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    users = User.query.all()
    trips = Trip.query.all()
    cities = City.query.all()
    activities = Activity.query.all()
    
    stats = {
        'total_users': len(users),
        'total_trips': len(trips),
        'total_cities': len(cities),
        'total_activities': len(activities)
    }
    
    return render_template('admin.html', users=users, trips=trips, cities=cities, activities=activities, stats=stats)


# Admin API Routes
@app.route('/admin/api/user/<user_id>', methods=['DELETE'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    # Delete all user's trips first
    Trip.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/trip/<trip_id>', methods=['DELETE'])
@admin_required
def admin_delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/city/<city_id>', methods=['DELETE'])
@admin_required
def admin_delete_city(city_id):
    city = City.query.get_or_404(city_id)
    # Delete all activities in this city first
    Activity.query.filter_by(city_id=city_id).delete()
    db.session.delete(city)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/api/activity/<activity_id>', methods=['DELETE'])
@admin_required
def admin_delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/city/add', methods=['POST'])
@admin_required
def admin_add_city():
    import uuid
    city = City(
        city_id=str(uuid.uuid4()),
        city_name=request.form.get('city_name'),
        state=request.form.get('state'),
        image_url=request.form.get('image_url', ''),
        description=request.form.get('description', '')
    )
    db.session.add(city)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/activity/add', methods=['POST'])
@admin_required
def admin_add_activity():
    import uuid
    activity = Activity(
        activity_id=str(uuid.uuid4()),
        activity_name=request.form.get('activity_name'),
        city_id=request.form.get('city_id'),
        activity_type=request.form.get('activity_type', 'sightseeing'),
        duration=request.form.get('duration', ''),
        cost=float(request.form.get('cost', 0)),
        description=request.form.get('description', '')
    )
    db.session.add(activity)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


# Initialize Database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized!")


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True, port=5001)
