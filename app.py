"""
Payanam - Indian Travel Itinerary Planner
A beautiful, UI-focused travel planning application for exploring India
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from models import db, User, Trip, City, Activity

app = Flask(__name__)
app.config['SECRET_KEY'] = 'payanam-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payanam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


# Initialize Database
def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized!")


# Seed Data: Cities and Activities from indianCities
SEED_DATA = {
    # ==================== RAJASTHAN (15 Cities) ====================
    'Jaipur': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1477587458883-47145ed94245?w=400',
        'activities': ['Amber Fort', 'Hawa Mahal', 'City Palace Jaipur', 'Nahargarh Fort', 'Jantar Mantar', 'Jal Mahal', 'Birla Mandir Jaipur', 'Albert Hall Museum', 'Johari Bazaar Shopping', 'Chokhi Dhani Village']
    },
    'Udaipur': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1568495248636-6432b97bd949?w=400',
        'activities': ['City Palace Udaipur', 'Lake Pichola Boat Ride', 'Jag Mandir Island', 'Sajjangarh Monsoon Palace', 'Fateh Sagar Lake', 'Bagore Ki Haveli', 'Vintage Car Museum', 'Jagdish Temple', 'Saheliyon Ki Bari', 'Shilpgram Craft Village']
    },
    'Jaisalmer': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1587135941948-670b381f08ce?w=400',
        'activities': ['Jaisalmer Fort', 'Sam Sand Dunes', 'Desert Camel Safari', 'Patwon Ki Haveli', 'Desert Camping Night', 'Gadisar Lake', 'Kuldhara Ghost Village', 'Bada Bagh Cenotaphs', 'Desert Cultural Show', 'Tanot Mata Temple']
    },
    'Jodhpur': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400',
        'activities': ['Mehrangarh Fort', 'Umaid Bhawan Palace', 'Jaswant Thada', 'Mandore Gardens', 'Clock Tower Market', 'Blue City Walking Tour', 'Rao Jodha Desert Park', 'Toorji Ka Jhalra Stepwell', 'Masuria Hills Garden', 'Flying Fox Zipline']
    },
    'Pushkar': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=400',
        'activities': ['Brahma Temple', 'Pushkar Lake Ghats', 'Savitri Temple Trek', 'Pushkar Camel Fair', 'Rose Garden Visit', 'Old Rangji Temple', 'Varaha Temple', 'Pushkar Bazaar Shopping', 'Sunset Point Hills', 'Cooking Class Experience']
    },
    'Bikaner': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1624461850043-dde2eafdb482?w=400',
        'activities': ['Junagarh Fort', 'Karni Mata Temple', 'Lalgarh Palace', 'Camel Research Centre', 'Bikaner Camel Safari', 'Rampuria Haveli', 'Gajner Palace', 'Bhujia Snack Tasting', 'Devi Kund Sagar', 'Ganga Golden Jubilee Museum']
    },
    'Mount Abu': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400',
        'activities': ['Dilwara Jain Temples', 'Nakki Lake Boating', 'Sunset Point', 'Guru Shikhar Peak', 'Achalgarh Fort', 'Wildlife Sanctuary Safari', 'Peace Park', 'Honeymoon Point', 'Toad Rock Viewpoint', 'Trevor Tank Lake']
    },
    'Ajmer': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1590766740554-f14a61e8b0a4?w=400',
        'activities': ['Ajmer Sharif Dargah', 'Ana Sagar Lake', 'Adhai Din Ka Jhonpra', 'Taragarh Fort', 'Akbari Mosque', 'Nareli Jain Temple', 'Foy Sagar Lake', 'Soniji Ki Nasiyan', 'Magazine Museum', 'Prithviraj Smarak']
    },
    'Bundi': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=400',
        'activities': ['Taragarh Fort Bundi', 'Bundi Palace', 'Raniji Ki Baori', 'Nawal Sagar Lake', 'Chitrashala Paintings', 'Sukh Mahal', '84 Pillared Cenotaph', 'Dabhai Kund Stepwell', 'Jait Sagar Lake', 'Phool Sagar Palace']
    },
    'Chittorgarh': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1623682242968-73e5e3eca697?w=400',
        'activities': ['Chittorgarh Fort', 'Vijay Stambha Tower', 'Kirti Stambha', 'Rana Kumbha Palace', 'Padmini Palace', 'Meera Temple', 'Gaumukh Reservoir', 'Kalika Mata Temple', 'Fateh Prakash Palace', 'Light and Sound Show']
    },
    'Ranthambore': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1549366021-9f761d450615?w=400',
        'activities': ['Tiger Safari Morning', 'Tiger Safari Evening', 'Ranthambore Fort', 'Padam Talao Lake', 'Jogi Mahal', 'Ganesh Temple', 'Surwal Lake Birds', 'Kachida Valley', 'Rajbagh Ruins', 'Wildlife Photography Tour']
    },
    'Alwar': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1600100397608-e4fbcbff3e5a?w=400',
        'activities': ['Bala Quila Fort', 'Sariska Tiger Reserve', 'Siliserh Lake Palace', 'Alwar City Palace', 'Moosi Maharani Chhatri', 'Government Museum', 'Bhangarh Fort', 'Neemrana Fort Palace', 'Vijay Mandir Palace', 'Pandupol Hanuman Temple']
    },
    'Bharatpur': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=400',
        'activities': ['Keoladeo Bird Sanctuary', 'Lohagarh Fort', 'Bharatpur Palace', 'Government Museum', 'Ganga Mandir', 'Laxman Temple', 'Deeg Palace Day Trip', 'Bird Photography Tour', 'Cycle Safari', 'Boat Ride in Sanctuary']
    },
    'Mandawa': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1590766940554-f14a61e8b0a4?w=400',
        'activities': ['Mandawa Fort', 'Haveli Heritage Walk', 'Murmuria Haveli', 'Hanuman Prasad Goenka Haveli', 'Gulab Rai Ladia Haveli', 'Jhunjhunwala Haveli', 'Open Air Art Gallery', 'Shekhawati Painting Tour', 'Camel Cart Ride', 'Village Cultural Tour']
    },
    'Sawai Madhopur': {
        'state': 'Rajasthan',
        'image': 'https://images.unsplash.com/photo-1574068468668-a05a11f871da?w=400',
        'activities': ['Ranthambore National Park', 'Trinetra Ganesh Temple', 'Ranthambore Fort', 'Khandar Fort', 'Chambal Safari', 'Malik Talao', 'Bakula', 'Lakarda and Anantpura', 'Raj Bagh Talao', 'Canter Safari Experience']
    },

    # ==================== TAMIL NADU (15 Cities) ====================
    'Chennai': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=400',
        'activities': ['Marina Beach Walk', 'Kapaleeshwarar Temple', 'Fort St. George', 'San Thome Cathedral', 'Government Museum', 'Valluvar Kottam', 'T Nagar Shopping', 'DakshinaChitra Heritage', 'Elliot Beach', 'Birla Planetarium']
    },
    'Madurai': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1590766940554-634931ab6293?w=400',
        'activities': ['Meenakshi Amman Temple', 'Thirumalai Nayakkar Palace', 'Gandhi Memorial Museum', 'Banana Market Visit', 'Jigarthanda Tasting', 'Alagar Kovil', 'Thirupparankundram Temple', 'Vandiyur Mariamman Teppakulam', 'Koodal Azhagar Temple', 'Pudhu Mandapam']
    },
    'Coimbatore': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1593181629936-11c609b8db9b?w=400',
        'activities': ['Isha Yoga Center', 'Dhyanalinga Meditation', 'Marudamalai Temple', 'VOC Park', 'Siruvani Waterfalls', 'Vellingiri Hills Trek', 'Perur Pateeswarar Temple', 'Gass Forest Museum', 'Brookefields Mall', 'Annapoorna Restaurant Experience']
    },
    'Ooty': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=400',
        'activities': ['Botanical Gardens', 'Ooty Lake Boating', 'Nilgiri Mountain Railway', 'Doddabetta Peak', 'Tea Factory Visit', 'Rose Garden', 'Pykara Falls', 'Avalanche Lake', 'Emerald Lake', 'Tribal Toda Village']
    },
    'Kodaikanal': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=400',
        'activities': ['Kodaikanal Lake Boating', 'Coakers Walk', 'Pillar Rocks', 'Bryant Park', 'Silver Cascade Falls', 'Pine Forest Walk', 'Green Valley View', 'Dolphins Nose Viewpoint', 'Guna Cave', 'Berijam Lake Safari']
    },
    'Thanjavur': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1621427639016-5e98ea93ca2f?w=400',
        'activities': ['Brihadeeswarar Temple', 'Thanjavur Maratha Palace', 'Saraswathi Mahal Library', 'Royal Museum', 'Schwartz Church', 'Sangeetha Mahal', 'Art Gallery Visit', 'Tanjore Painting Workshop', 'Sivaganga Park', 'Alangudi Guru Temple']
    },
    'Rameswaram': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1621427639016-5e98ea93ca2f?w=400',
        'activities': ['Ramanathaswamy Temple', 'Pamban Bridge Views', 'Dhanushkodi Ghost Town', 'Agni Theertham', 'Five-faced Hanuman Temple', 'APJ Abdul Kalam Memorial', 'Gandhamadhana Parvatham', 'Ariyaman Beach', 'Villoondi Theertham', 'Lakshmana Theertham']
    },
    'Kanyakumari': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1590766940554-f14a61e8b0a4?w=400',
        'activities': ['Vivekananda Rock Memorial', 'Thiruvalluvar Statue', 'Sunrise and Sunset Point', 'Padmanabhapuram Palace', 'Suchindram Temple', 'Kanyakumari Beach', 'Gandhi Memorial Mandapam', 'Wax Museum', 'Bhagavathy Amman Temple', 'Thirparappu Falls']
    },
    'Tiruchirappalli': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=400',
        'activities': ['Rock Fort Temple', 'Sri Ranganathaswamy Temple', 'Jambukeswarar Temple', 'St. Josephs Church', 'Kallanai Dam', 'Government Museum', 'Mukkombu Picnic', 'Amma Mandapam', 'Ucchi Pillayar Temple', 'Lourdes Church']
    },
    'Mahabalipuram': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=400',
        'activities': ['Shore Temple', 'Pancha Rathas', 'Arjunas Penance', 'Krishna Butter Ball', 'Mahabalipuram Beach', 'Tiger Cave', 'Crocodile Bank', 'Sculpture Workshop', 'Light and Sound Show', 'Mahishasuramardini Cave']
    },
    'Pondicherry': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1580292923498-e3c52ada76a4?w=400',
        'activities': ['Promenade Beach Walk', 'Auroville Matrimandir', 'French Colony Heritage Walk', 'Sri Aurobindo Ashram', 'Paradise Beach', 'Serenity Beach', 'Basilica of Sacred Heart', 'Pondicherry Museum', 'Botanical Garden', 'Arikamedu Archaeological Site']
    },
    'Tirunelveli': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1590766940554-634931ab6293?w=400',
        'activities': ['Nellaiappar Temple', 'Krishnapuram Palace', 'Courtallam Falls', 'Manimuthar Dam', 'Papanasam Falls', 'Agasthiyar Falls', 'Tiruchendur Temple', 'Kalakkad Tiger Reserve', 'Banana Chips Shopping', 'Halwa Tasting']
    },
    'Salem': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400',
        'activities': ['Yercaud Hill Station', 'Kottai Mariamman Temple', 'Sugavaneswarar Temple', 'Salem Steel Plant Tour', 'Kiliyur Falls', 'Ladies Seat Viewpoint', 'Anna Park', 'Pagoda Point', 'Mettur Dam', 'Shevaroy Temple']
    },
    'Vellore': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1600100397608-e4fbcbff3e5a?w=400',
        'activities': ['Vellore Fort', 'Golden Temple Sripuram', 'Jalakandeswarar Temple', 'Government Museum', 'Amirthi Zoological Park', 'Science Park', 'Yelagiri Hills Day Trip', 'CMC Hospital Heritage', 'VIT Campus Visit', 'Ratnagiri Murugan Temple']
    },
    'Kanchipuram': {
        'state': 'Tamil Nadu',
        'image': 'https://images.unsplash.com/photo-1590766940554-634931ab6293?w=400',
        'activities': ['Kailasanathar Temple', 'Ekambareswarar Temple', 'Kamakshi Amman Temple', 'Varadharaja Perumal Temple', 'Silk Saree Shopping', 'Kanchi Kudil Heritage', 'Vaikunta Perumal Temple', 'Kailasanathar Sculptures', 'Vedanthangal Bird Sanctuary', 'Silk Weaving Demonstration']
    },

    # ==================== KERALA (15 Cities) ====================
    'Kochi': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
        'activities': ['Fort Kochi Heritage Walk', 'Chinese Fishing Nets', 'Mattancherry Palace', 'Jewish Synagogue', 'Kerala Kathakali Show', 'Marine Drive Promenade', 'Lulu Mall Shopping', 'St. Francis Church', 'Jew Town Antique Shopping', 'Kerala Cooking Class']
    },
    'Alleppey': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=400',
        'activities': ['Houseboat Overnight Stay', 'Backwater Cruise', 'Alleppey Beach', 'Ambalapuzha Temple', 'Coir Village Visit', 'Kayaking Backwaters', 'Pathiramanal Island', 'Marari Beach', 'Krishnapuram Palace', 'Nehru Trophy Snake Boat']
    },
    'Munnar': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1549880338-65ddcdfd017b?w=400',
        'activities': ['Tea Gardens Walk', 'Eravikulam National Park', 'Mattupetty Dam', 'Echo Point', 'Tea Museum Visit', 'Top Station Viewpoint', 'Anamudi Peak View', 'Attukal Waterfalls', 'Kundala Lake', 'Rose Garden Munnar']
    },
    'Thekkady': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=400',
        'activities': ['Periyar Wildlife Sanctuary', 'Periyar Lake Boat Safari', 'Spice Plantation Tour', 'Elephant Junction', 'Bamboo Rafting', 'Jungle Night Patrol', 'Tribal Heritage Museum', 'Kadathanadan Kalari Center', 'Mangala Devi Temple', 'Chellarkovil Viewpoint']
    },
    'Wayanad': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=400',
        'activities': ['Edakkal Caves', 'Banasura Sagar Dam', 'Chembra Peak Trek', 'Soochipara Waterfalls', 'Thirunelli Temple', 'Wayanad Wildlife Sanctuary', 'Pookode Lake', 'Kuruva Island', 'Neelimala Viewpoint', 'Coffee Plantation Tour']
    },
    'Thiruvananthapuram': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
        'activities': ['Padmanabhaswamy Temple', 'Kovalam Beach', 'Napier Museum', 'Veli Tourist Village', 'Poovar Island', 'Kuthiramalika Palace', 'Science and Technology Museum', 'Priyadarshini Planetarium', 'Neyyar Dam', 'Agasthyakoodam Trek']
    },
    'Kovalam': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
        'activities': ['Lighthouse Beach', 'Hawa Beach', 'Samudra Beach', 'Ayurvedic Massage Spa', 'Vizhinjam Rock Cut Cave', 'Vizhinjam Fishing Village', 'Surfing Lessons', 'Yoga Retreat', 'Parasailing Adventure', 'Lighthouse Climb']
    },
    'Kumarakom': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=400',
        'activities': ['Kumarakom Bird Sanctuary', 'Vembanad Lake Cruise', 'Houseboat Stay', 'Ayurvedic Resort', 'Bay Island Driftwood Museum', 'Aruvikkuzhi Waterfall', 'Kumarakom Beach', 'Thazhathangadi Mosque', 'Fishing Experience', 'Sunset Village Walk']
    },
    'Varkala': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
        'activities': ['Varkala Beach Cliff Walk', 'Papanasam Beach', 'Janardhanaswamy Temple', 'Sivagiri Mutt', 'Kappil Beach', 'Edava Beach', 'Varkala Tunnel', 'Ayurveda Treatment', 'Cliff Top Cafes', 'Yoga on the Beach']
    },
    'Thrissur': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
        'activities': ['Vadakkunnathan Temple', 'Thrissur Pooram Festival', 'Athirappilly Falls', 'Vazhachal Falls', 'Shakthan Thampuran Palace', 'Kerala Kalamandalam', 'Peechi Dam', 'Kerala Folklore Museum', 'Guruvayur Temple', 'Chettuva Backwaters']
    },
    'Kozhikode': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
        'activities': ['Kozhikode Beach', 'Mananchira Square', 'Thusharagiri Waterfalls', 'Kappad Beach', 'SM Street Shopping', 'Mishkals Mosque', 'Pazhassi Raja Museum', 'Sweet Meat Street', 'Beypore Beach', 'Kadalundi Bird Sanctuary']
    },
    'Kannur': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
        'activities': ['St Angelos Fort', 'Payyambalam Beach', 'Muzhappilangad Drive-in Beach', 'Theyyam Ritual Performance', 'Kannur Lighthouse', 'Arakkal Museum', 'Dharmadam Island', 'Parassinikadavu Snake Park', 'Handloom Weaving Centre', 'Meenkunnu Beach']
    },
    'Palakkad': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=400',
        'activities': ['Palakkad Fort', 'Silent Valley National Park', 'Malampuzha Dam', 'Fantasy Park', 'Rock Garden', 'Parambikulam Tiger Reserve', 'Nelliyampathy Hills', 'Dhoni Waterfalls', 'Kalpathy Heritage Village', 'Jain Temple Jainimedu']
    },
    'Athirappilly': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=400',
        'activities': ['Athirappilly Waterfalls', 'Vazhachal Waterfalls', 'Charpa Falls', 'Sholayar Dam', 'Anakkayam Forest', 'Thumboormuzhi Dam', 'Peringalkuthu Dam', 'Rainforest Trek', 'Bamboo Rafting', 'Bird Watching Tour']
    },
    'Bekal': {
        'state': 'Kerala',
        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
        'activities': ['Bekal Fort', 'Bekal Beach', 'Kappil Beach', 'Nityanandashram Cave', 'Chandragiri Fort', 'Ananthapura Lake Temple', 'Bekal Hole Aqua Park', 'Backwater Cruise', 'Valiyaparamba Backwaters', 'Malik Dinar Mosque']
    },

    # ==================== OTHER STATES ====================
    # Goa
    'Goa': {
        'state': 'Goa',
        'image': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=400',
        'activities': ['Baga Beach', 'Calangute Beach', 'Aguada Fort', 'Basilica of Bom Jesus', 'Dudhsagar Falls', 'Saturday Night Market', 'Casino Night', 'Water Sports', 'Old Goa Churches', 'Spice Plantation Tour']
    },
    'Panaji': {
        'state': 'Goa',
        'image': 'https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=400',
        'activities': ['Fontainhas Latin Quarter', 'Church of Our Lady', 'Miramar Beach', 'Casino Cruise', 'Dona Paula', 'Goa State Museum', 'Reis Magos Fort', 'Mandovi River Cruise', 'Chapel of St Sebastian', 'Municipal Garden']
    },

    # Karnataka
    'Bangalore': {
        'state': 'Karnataka',
        'image': 'https://images.unsplash.com/photo-1596176530529-78163a4f7af2?w=400',
        'activities': ['Lalbagh Botanical Garden', 'Cubbon Park', 'Bangalore Palace', 'UB City Mall', 'Nandi Hills Day Trip', 'Brigade Road Shopping', 'Tipu Sultans Palace', 'ISKCON Temple', 'Innovative Film City', 'Bannerghatta Safari']
    },
    'Mysore': {
        'state': 'Karnataka',
        'image': 'https://images.unsplash.com/photo-1600100397608-e4fbcbff3e5a?w=400',
        'activities': ['Mysore Palace', 'Chamundi Hills', 'Brindavan Gardens', 'St. Philomenas Church', 'Mysore Zoo', 'Devaraja Market', 'Jaganmohan Palace', 'Karanji Lake', 'GRS Fantasy Park', 'Silk Factory Tour']
    },
    'Hampi': {
        'state': 'Karnataka',
        'image': 'https://images.unsplash.com/photo-1600100397608-e4fbcbff3e5a?w=400',
        'activities': ['Virupaksha Temple', 'Vittala Temple', 'Elephant Stables', 'Hampi Bazaar', 'Coracle Ride', 'Matanga Hill Sunrise', 'Lotus Mahal', 'Queens Bath', 'Hemakuta Hill', 'Underground Shiva Temple']
    },

    # Maharashtra
    'Mumbai': {
        'state': 'Maharashtra',
        'image': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=400',
        'activities': ['Gateway of India', 'Marine Drive', 'Elephanta Caves', 'Colaba Causeway', 'Siddhivinayak Temple', 'Juhu Beach', 'Film City Tour', 'Crawford Market', 'Haji Ali Dargah', 'Dharavi Tour']
    },
    'Pune': {
        'state': 'Maharashtra',
        'image': 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=400',
        'activities': ['Shaniwar Wada', 'Aga Khan Palace', 'Sinhagad Fort', 'Osho Ashram', 'Dagdusheth Halwai Ganpati', 'Raja Dinkar Kelkar Museum', 'Pataleshwar Cave Temple', 'Lavasa City', 'Lonavala Day Trip', 'Mahabaleshwar Trip']
    },

    # Others
    'Agra': {
        'state': 'Uttar Pradesh',
        'image': 'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=400',
        'activities': ['Taj Mahal', 'Agra Fort', 'Fatehpur Sikri', 'Mehtab Bagh', 'Itimad-ud-Daulah', 'Kinari Bazaar', 'Akbars Tomb', 'Jama Masjid Agra', 'Taj Museum', 'Marble Handicraft']
    },
    'Varanasi': {
        'state': 'Uttar Pradesh',
        'image': 'https://images.unsplash.com/photo-1561361513-2d000a50f0dc?w=400',
        'activities': ['Ganga Aarti', 'Boat Ride on Ganges', 'Kashi Vishwanath Temple', 'Sarnath', 'Dashashwamedh Ghat', 'Assi Ghat', 'Manikarnika Ghat', 'BHU Campus', 'Ramnagar Fort', 'Silk Weaving Tour']
    },
    'Delhi': {
        'state': 'Delhi',
        'image': 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=400',
        'activities': ['Red Fort', 'Qutub Minar', 'India Gate', 'Lotus Temple', 'Humayuns Tomb', 'Chandni Chowk', 'Akshardham Temple', 'Jama Masjid', 'Gurudwara Bangla Sahib', 'Hauz Khas Village']
    },
    'Shimla': {
        'state': 'Himachal Pradesh',
        'image': 'https://images.unsplash.com/photo-1597074866923-dc0589150358?w=400',
        'activities': ['Mall Road', 'Ridge', 'Jakhoo Temple', 'Christ Church', 'Toy Train Ride', 'Kufri', 'Green Valley', 'Viceregal Lodge', 'Annandale', 'Chadwick Falls']
    },
    'Manali': {
        'state': 'Himachal Pradesh',
        'image': 'https://images.unsplash.com/photo-1593181629936-11c609b8db9b?w=400',
        'activities': ['Rohtang Pass', 'Solang Valley', 'Hadimba Temple', 'Mall Road Manali', 'River Rafting Beas', 'Old Manali Cafes', 'Vashisht Hot Springs', 'Jogini Waterfall', 'Manu Temple', 'Tibetan Monastery']
    },
    'Rishikesh': {
        'state': 'Uttarakhand',
        'image': 'https://images.unsplash.com/photo-1586439738618-1142c0cec81f?w=400',
        'activities': ['Laxman Jhula', 'River Rafting', 'Ganga Aarti at Parmarth', 'Beatles Ashram', 'Bungee Jumping', 'Yoga Session', 'Ram Jhula', 'Neer Garh Waterfall', 'Triveni Ghat', 'Camping Riverside']
    },
    'Darjeeling': {
        'state': 'West Bengal',
        'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=400',
        'activities': ['Tiger Hill Sunrise', 'Toy Train Ride', 'Tea Garden Visit', 'Peace Pagoda', 'Batasia Loop', 'Happy Valley Tea Estate', 'Himalayan Mountaineering Institute', 'Padmaja Naidu Zoo', 'Rock Garden', 'Ghoom Monastery']
    }
}


def seed_cities_and_activities():
    """Populate the database with Indian cities and activities"""
    with app.app_context():
        for city_name, data in SEED_DATA.items():
            # Check if city exists
            existing_city = City.query.filter_by(name=city_name).first()
            if existing_city:
                print(f"City {city_name} already exists, skipping...")
                continue
            
            # Create city
            city = City(
                name=city_name,
                state=data['state'],
                image_url=data.get('image', ''),
                description=f"Beautiful city in {data['state']}, India",
                popular_score=len(data['activities'])  # More activities = more popular
            )
            db.session.add(city)
            db.session.flush()  # Get the city_id
            
            # Add activities
            for activity_name in data['activities']:
                activity = Activity(
                    city_id=city.city_id,
                    name=activity_name,
                    description=f"Popular activity in {city_name}",
                    rating=4.0
                )
                db.session.add(activity)
            
            print(f"Added {city_name} with {len(data['activities'])} activities")
        
        db.session.commit()
        print("Seed data added successfully!")


# API endpoint to seed data
@app.route('/api/seed-cities')
def api_seed_cities():
    """Seed the database with Indian cities and activities"""
    try:
        seed_cities_and_activities()
        return jsonify({'success': True, 'message': 'Cities and activities seeded successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
