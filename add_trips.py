"""
Script to add sample trips for testing
Creates 4 complete trips with detailed itineraries for different categories

JSON Format Expected by Templates:
- activity.activity_name (not 'name')
- activity.estimated_cost (not 'cost')
- day.day_number (required)
- stop.stop_category (array)
"""

from app import app, db
from models import User, Trip
import json
import uuid

def create_sample_trips():
    with app.app_context():
        # Find the user
        user = User.query.filter_by(email='mani.ks1324579@gmail.com').first()
        
        if not user:
            print("Error: User not found!")
            return
        
        user_id = user.user_id
        print(f"Creating trips for user: {user.name} ({user.email})")
        
        # Delete existing trips for this user to avoid duplicates
        existing_trips = Trip.query.filter_by(user_id=user_id).all()
        for trip in existing_trips:
            db.session.delete(trip)
        db.session.commit()
        print(f"Deleted {len(existing_trips)} existing trips")
        
        # Trip 1: Rajasthan Heritage Tour (heritage category)
        trip1 = Trip(
            trip_id=str(uuid.uuid4()),
            user_id=user_id,
            trip_name='Royal Rajasthan Heritage Tour',
            trip_description='A majestic journey through the royal palaces, magnificent forts, and vibrant culture of Rajasthan - the land of kings.',
            trip_category='heritage',
            cover_image='https://images.unsplash.com/photo-1477587458883-47145ed94245?w=800',
            start_date='2026-02-01',
            end_date='2026-02-10',
            total_budget=45000,
            is_public=True,
            itinerary_json=json.dumps({
                'stops': [
                    {
                        'city_name': 'Jaipur',
                        'state': 'Rajasthan',
                        'arrival_date': '2026-02-01',
                        'departure_date': '2026-02-03',
                        'image': 'https://images.unsplash.com/photo-1477587458883-47145ed94245?w=400',
                        'stop_category': ['heritage', 'culture'],
                        'days': [
                            {'day_number': 1, 'date': '2026-02-01', 'activities': [
                                {'activity_name': 'Amber Fort', 'time': '09:00', 'duration': '3 hours', 'estimated_cost': 500, 'category': 'heritage', 'notes': 'Elephant ride available'},
                                {'activity_name': 'Hawa Mahal', 'time': '13:00', 'duration': '1 hour', 'estimated_cost': 200, 'category': 'heritage', 'notes': 'Best photos in morning light'},
                                {'activity_name': 'City Palace Jaipur', 'time': '15:00', 'duration': '2 hours', 'estimated_cost': 500, 'category': 'heritage', 'notes': 'Royal museum inside'}
                            ]},
                            {'day_number': 2, 'date': '2026-02-02', 'activities': [
                                {'activity_name': 'Nahargarh Fort', 'time': '06:00', 'duration': '2 hours', 'estimated_cost': 200, 'category': 'sightseeing', 'notes': 'Sunrise view'},
                                {'activity_name': 'Jantar Mantar', 'time': '10:00', 'duration': '1.5 hours', 'estimated_cost': 200, 'category': 'heritage', 'notes': 'UNESCO World Heritage'},
                                {'activity_name': 'Johari Bazaar Shopping', 'time': '16:00', 'duration': '3 hours', 'estimated_cost': 0, 'category': 'shopping', 'notes': 'Famous for jewelry'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Jodhpur',
                        'state': 'Rajasthan',
                        'arrival_date': '2026-02-03',
                        'departure_date': '2026-02-05',
                        'image': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400',
                        'stop_category': ['heritage', 'culture'],
                        'days': [
                            {'day_number': 3, 'date': '2026-02-03', 'activities': [
                                {'activity_name': 'Mehrangarh Fort', 'time': '09:00', 'duration': '4 hours', 'estimated_cost': 600, 'category': 'heritage', 'notes': 'One of Indias largest forts'},
                                {'activity_name': 'Jaswant Thada', 'time': '14:00', 'duration': '1 hour', 'estimated_cost': 30, 'category': 'heritage', 'notes': 'Marble memorial'}
                            ]},
                            {'day_number': 4, 'date': '2026-02-04', 'activities': [
                                {'activity_name': 'Blue City Walking Tour', 'time': '07:00', 'duration': '3 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Through old city'},
                                {'activity_name': 'Umaid Bhawan Palace', 'time': '11:00', 'duration': '2 hours', 'estimated_cost': 100, 'category': 'heritage', 'notes': 'Still a royal residence'},
                                {'activity_name': 'Clock Tower Market', 'time': '17:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'shopping', 'notes': 'Local spices'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Jaisalmer',
                        'state': 'Rajasthan',
                        'arrival_date': '2026-02-05',
                        'departure_date': '2026-02-08',
                        'image': 'https://images.unsplash.com/photo-1587135941948-670b381f08ce?w=400',
                        'stop_category': ['heritage', 'adventure'],
                        'days': [
                            {'day_number': 5, 'date': '2026-02-05', 'activities': [
                                {'activity_name': 'Jaisalmer Fort', 'time': '10:00', 'duration': '3 hours', 'estimated_cost': 100, 'category': 'heritage', 'notes': 'Living fort with shops'},
                                {'activity_name': 'Patwon Ki Haveli', 'time': '14:00', 'duration': '1.5 hours', 'estimated_cost': 100, 'category': 'heritage', 'notes': 'Intricate carvings'}
                            ]},
                            {'day_number': 6, 'date': '2026-02-06', 'activities': [
                                {'activity_name': 'Sam Sand Dunes', 'time': '15:00', 'duration': '5 hours', 'estimated_cost': 2000, 'category': 'adventure', 'notes': 'Camel safari at sunset'},
                                {'activity_name': 'Desert Camping Night', 'time': '20:00', 'duration': '12 hours', 'estimated_cost': 3000, 'category': 'adventure', 'notes': 'Under the stars'}
                            ]},
                            {'day_number': 7, 'date': '2026-02-07', 'activities': [
                                {'activity_name': 'Gadisar Lake', 'time': '06:00', 'duration': '2 hours', 'estimated_cost': 50, 'category': 'sightseeing', 'notes': 'Sunrise boating'},
                                {'activity_name': 'Kuldhara Ghost Village', 'time': '10:00', 'duration': '2 hours', 'estimated_cost': 50, 'category': 'heritage', 'notes': 'Abandoned village'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Udaipur',
                        'state': 'Rajasthan',
                        'arrival_date': '2026-02-08',
                        'departure_date': '2026-02-10',
                        'image': 'https://images.unsplash.com/photo-1568495248636-6432b97bd949?w=400',
                        'stop_category': ['heritage', 'romantic'],
                        'days': [
                            {'day_number': 8, 'date': '2026-02-08', 'activities': [
                                {'activity_name': 'City Palace Udaipur', 'time': '09:00', 'duration': '3 hours', 'estimated_cost': 300, 'category': 'heritage', 'notes': 'Largest palace in Rajasthan'},
                                {'activity_name': 'Lake Pichola Boat Ride', 'time': '16:00', 'duration': '1.5 hours', 'estimated_cost': 400, 'category': 'sightseeing', 'notes': 'Sunset views'}
                            ]},
                            {'day_number': 9, 'date': '2026-02-09', 'activities': [
                                {'activity_name': 'Jag Mandir Island', 'time': '10:00', 'duration': '2 hours', 'estimated_cost': 500, 'category': 'heritage', 'notes': 'Island palace'},
                                {'activity_name': 'Sajjangarh Monsoon Palace', 'time': '16:00', 'duration': '2 hours', 'estimated_cost': 200, 'category': 'sightseeing', 'notes': 'Hilltop palace'},
                                {'activity_name': 'Bagore Ki Haveli', 'time': '19:00', 'duration': '2 hours', 'estimated_cost': 150, 'category': 'sightseeing', 'notes': 'Cultural dance show'}
                            ]}
                        ]
                    }
                ]
            })
        )
        db.session.add(trip1)
        print("✓ Created Trip 1: Royal Rajasthan Heritage Tour")

        # Trip 2: Kerala Backwaters & Nature (nature category)
        trip2 = Trip(
            trip_id=str(uuid.uuid4()),
            user_id=user_id,
            trip_name='Kerala - Gods Own Country',
            trip_description='Experience the serene backwaters, misty hill stations, wildlife sanctuaries, and pristine beaches of Kerala.',
            trip_category='nature',
            cover_image='https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800',
            start_date='2026-03-15',
            end_date='2026-03-24',
            total_budget=55000,
            is_public=True,
            itinerary_json=json.dumps({
                'stops': [
                    {
                        'city_name': 'Kochi',
                        'state': 'Kerala',
                        'arrival_date': '2026-03-15',
                        'departure_date': '2026-03-17',
                        'image': 'https://images.unsplash.com/photo-1590050751537-eb45b8c0c9f4?w=400',
                        'stop_category': ['heritage', 'culture'],
                        'days': [
                            {'day_number': 1, 'date': '2026-03-15', 'activities': [
                                {'activity_name': 'Fort Kochi Heritage Walk', 'time': '09:00', 'duration': '3 hours', 'estimated_cost': 0, 'category': 'heritage', 'notes': 'Colonial architecture'},
                                {'activity_name': 'Chinese Fishing Nets', 'time': '17:00', 'duration': '1 hour', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Sunset photography'}
                            ]},
                            {'day_number': 2, 'date': '2026-03-16', 'activities': [
                                {'activity_name': 'Mattancherry Palace', 'time': '10:00', 'duration': '1.5 hours', 'estimated_cost': 10, 'category': 'heritage', 'notes': 'Dutch Palace'},
                                {'activity_name': 'Jewish Synagogue', 'time': '12:00', 'duration': '1 hour', 'estimated_cost': 5, 'category': 'heritage', 'notes': 'Oldest in Commonwealth'},
                                {'activity_name': 'Kerala Kathakali Show', 'time': '18:00', 'duration': '2 hours', 'estimated_cost': 350, 'category': 'sightseeing', 'notes': 'Traditional dance'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Alleppey',
                        'state': 'Kerala',
                        'arrival_date': '2026-03-17',
                        'departure_date': '2026-03-19',
                        'image': 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=400',
                        'stop_category': ['nature', 'relaxation'],
                        'days': [
                            {'day_number': 3, 'date': '2026-03-17', 'activities': [
                                {'activity_name': 'Houseboat Overnight Stay', 'time': '12:00', 'duration': '24 hours', 'estimated_cost': 8000, 'category': 'relaxation', 'notes': 'Backwater cruise with meals'},
                                {'activity_name': 'Backwater Cruise', 'time': '14:00', 'duration': '6 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Included in houseboat'}
                            ]},
                            {'day_number': 4, 'date': '2026-03-18', 'activities': [
                                {'activity_name': 'Alleppey Beach', 'time': '06:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Morning walk'},
                                {'activity_name': 'Coir Village Visit', 'time': '10:00', 'duration': '2 hours', 'estimated_cost': 100, 'category': 'sightseeing', 'notes': 'Coir making process'},
                                {'activity_name': 'Kayaking Backwaters', 'time': '15:00', 'duration': '3 hours', 'estimated_cost': 1500, 'category': 'adventure', 'notes': 'Through narrow canals'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Thekkady',
                        'state': 'Kerala',
                        'arrival_date': '2026-03-19',
                        'departure_date': '2026-03-21',
                        'image': 'https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=400',
                        'stop_category': ['nature', 'adventure'],
                        'days': [
                            {'day_number': 5, 'date': '2026-03-19', 'activities': [
                                {'activity_name': 'Periyar Wildlife Sanctuary', 'time': '07:00', 'duration': '4 hours', 'estimated_cost': 500, 'category': 'adventure', 'notes': 'Boat safari'},
                                {'activity_name': 'Spice Plantation Tour', 'time': '14:00', 'duration': '3 hours', 'estimated_cost': 500, 'category': 'sightseeing', 'notes': 'Cardamom, pepper, coffee'}
                            ]},
                            {'day_number': 6, 'date': '2026-03-20', 'activities': [
                                {'activity_name': 'Bamboo Rafting', 'time': '07:00', 'duration': '3 hours', 'estimated_cost': 1500, 'category': 'adventure', 'notes': 'In Periyar Tiger Reserve'},
                                {'activity_name': 'Elephant Junction', 'time': '14:00', 'duration': '2 hours', 'estimated_cost': 800, 'category': 'sightseeing', 'notes': 'Elephant interaction'},
                                {'activity_name': 'Kadathanadan Kalari Center', 'time': '18:00', 'duration': '1.5 hours', 'estimated_cost': 300, 'category': 'sightseeing', 'notes': 'Martial arts show'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Munnar',
                        'state': 'Kerala',
                        'arrival_date': '2026-03-21',
                        'departure_date': '2026-03-24',
                        'image': 'https://images.unsplash.com/photo-1549880338-65ddcdfd017b?w=400',
                        'stop_category': ['nature', 'relaxation'],
                        'days': [
                            {'day_number': 7, 'date': '2026-03-21', 'activities': [
                                {'activity_name': 'Tea Gardens Walk', 'time': '08:00', 'duration': '3 hours', 'estimated_cost': 200, 'category': 'sightseeing', 'notes': 'Scenic tea estates'},
                                {'activity_name': 'Tea Museum Visit', 'time': '14:00', 'duration': '2 hours', 'estimated_cost': 125, 'category': 'sightseeing', 'notes': 'Tea processing'}
                            ]},
                            {'day_number': 8, 'date': '2026-03-22', 'activities': [
                                {'activity_name': 'Eravikulam National Park', 'time': '07:00', 'duration': '4 hours', 'estimated_cost': 175, 'category': 'adventure', 'notes': 'Nilgiri Tahr sighting'},
                                {'activity_name': 'Mattupetty Dam', 'time': '14:00', 'duration': '2 hours', 'estimated_cost': 50, 'category': 'sightseeing', 'notes': 'Boating available'}
                            ]},
                            {'day_number': 9, 'date': '2026-03-23', 'activities': [
                                {'activity_name': 'Top Station Viewpoint', 'time': '05:00', 'duration': '4 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Sunrise point'},
                                {'activity_name': 'Echo Point', 'time': '11:00', 'duration': '1 hour', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Natural echo'},
                                {'activity_name': 'Attukal Waterfalls', 'time': '15:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Scenic waterfall'}
                            ]}
                        ]
                    }
                ]
            })
        )
        db.session.add(trip2)
        print("✓ Created Trip 2: Kerala - Gods Own Country")

        # Trip 3: Tamil Nadu Temple Trail (pilgrimage category)
        trip3 = Trip(
            trip_id=str(uuid.uuid4()),
            user_id=user_id,
            trip_name='Tamil Nadu Divine Temple Trail',
            trip_description='A spiritual journey through the magnificent Dravidian temples of Tamil Nadu, exploring ancient architecture and rich traditions.',
            trip_category='pilgrimage',
            cover_image='https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=800',
            start_date='2026-04-10',
            end_date='2026-04-18',
            total_budget=35000,
            is_public=True,
            itinerary_json=json.dumps({
                'stops': [
                    {
                        'city_name': 'Chennai',
                        'state': 'Tamil Nadu',
                        'arrival_date': '2026-04-10',
                        'departure_date': '2026-04-12',
                        'image': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=400',
                        'stop_category': ['heritage', 'culture'],
                        'days': [
                            {'day_number': 1, 'date': '2026-04-10', 'activities': [
                                {'activity_name': 'Kapaleeshwarar Temple', 'time': '06:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Ancient Shiva temple'},
                                {'activity_name': 'San Thome Cathedral', 'time': '10:00', 'duration': '1 hour', 'estimated_cost': 0, 'category': 'heritage', 'notes': 'St. Thomas tomb'},
                                {'activity_name': 'Marina Beach Walk', 'time': '17:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Longest urban beach'}
                            ]},
                            {'day_number': 2, 'date': '2026-04-11', 'activities': [
                                {'activity_name': 'Fort St. George', 'time': '09:00', 'duration': '2 hours', 'estimated_cost': 50, 'category': 'heritage', 'notes': 'First British fort'},
                                {'activity_name': 'Government Museum', 'time': '12:00', 'duration': '2 hours', 'estimated_cost': 50, 'category': 'heritage', 'notes': 'Bronze gallery'},
                                {'activity_name': 'DakshinaChitra Heritage', 'time': '15:00', 'duration': '3 hours', 'estimated_cost': 200, 'category': 'heritage', 'notes': 'South Indian culture'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Mahabalipuram',
                        'state': 'Tamil Nadu',
                        'arrival_date': '2026-04-12',
                        'departure_date': '2026-04-13',
                        'image': 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=400',
                        'stop_category': ['heritage'],
                        'days': [
                            {'day_number': 3, 'date': '2026-04-12', 'activities': [
                                {'activity_name': 'Shore Temple', 'time': '06:00', 'duration': '1.5 hours', 'estimated_cost': 40, 'category': 'heritage', 'notes': 'UNESCO site, sunrise'},
                                {'activity_name': 'Pancha Rathas', 'time': '09:00', 'duration': '1.5 hours', 'estimated_cost': 40, 'category': 'heritage', 'notes': 'Five monolithic chariots'},
                                {'activity_name': 'Arjunas Penance', 'time': '11:00', 'duration': '1 hour', 'estimated_cost': 0, 'category': 'heritage', 'notes': 'Giant rock relief'},
                                {'activity_name': 'Krishna Butter Ball', 'time': '12:30', 'duration': '30 mins', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Balancing boulder'},
                                {'activity_name': 'Mahabalipuram Beach', 'time': '17:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Seafood dinner'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Thanjavur',
                        'state': 'Tamil Nadu',
                        'arrival_date': '2026-04-13',
                        'departure_date': '2026-04-15',
                        'image': 'https://images.unsplash.com/photo-1621427639016-5e98ea93ca2f?w=400',
                        'stop_category': ['heritage', 'culture'],
                        'days': [
                            {'day_number': 4, 'date': '2026-04-13', 'activities': [
                                {'activity_name': 'Brihadeeswarar Temple', 'time': '06:00', 'duration': '3 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'UNESCO Big Temple'},
                                {'activity_name': 'Thanjavur Maratha Palace', 'time': '10:00', 'duration': '2 hours', 'estimated_cost': 50, 'category': 'heritage', 'notes': 'Royal complex'}
                            ]},
                            {'day_number': 5, 'date': '2026-04-14', 'activities': [
                                {'activity_name': 'Saraswathi Mahal Library', 'time': '10:00', 'duration': '1.5 hours', 'estimated_cost': 50, 'category': 'heritage', 'notes': 'Ancient manuscripts'},
                                {'activity_name': 'Tanjore Painting Workshop', 'time': '14:00', 'duration': '3 hours', 'estimated_cost': 500, 'category': 'sightseeing', 'notes': 'Traditional art'},
                                {'activity_name': 'Schwartz Church', 'time': '17:00', 'duration': '1 hour', 'estimated_cost': 0, 'category': 'heritage', 'notes': 'Historic church'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Madurai',
                        'state': 'Tamil Nadu',
                        'arrival_date': '2026-04-15',
                        'departure_date': '2026-04-18',
                        'image': 'https://images.unsplash.com/photo-1590766940554-634931ab6293?w=400',
                        'stop_category': ['heritage', 'culture'],
                        'days': [
                            {'day_number': 6, 'date': '2026-04-15', 'activities': [
                                {'activity_name': 'Meenakshi Amman Temple', 'time': '05:00', 'duration': '4 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Iconic 14 gopurams'},
                                {'activity_name': 'Thirumalai Nayakkar Palace', 'time': '10:00', 'duration': '1.5 hours', 'estimated_cost': 50, 'category': 'heritage', 'notes': 'Indo-Saracenic'}
                            ]},
                            {'day_number': 7, 'date': '2026-04-16', 'activities': [
                                {'activity_name': 'Gandhi Memorial Museum', 'time': '10:00', 'duration': '2 hours', 'estimated_cost': 10, 'category': 'heritage', 'notes': 'Historical exhibits'},
                                {'activity_name': 'Banana Market Visit', 'time': '06:00', 'duration': '1.5 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Early morning market'},
                                {'activity_name': 'Jigarthanda Tasting', 'time': '16:00', 'duration': '1 hour', 'estimated_cost': 100, 'category': 'food', 'notes': 'Famous local drink'}
                            ]},
                            {'day_number': 8, 'date': '2026-04-17', 'activities': [
                                {'activity_name': 'Alagar Kovil', 'time': '07:00', 'duration': '3 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Hill temple'},
                                {'activity_name': 'Thirupparankundram Temple', 'time': '14:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Murugan temple'},
                                {'activity_name': 'Vandiyur Mariamman Teppakulam', 'time': '17:00', 'duration': '1.5 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Temple tank'}
                            ]}
                        ]
                    }
                ]
            })
        )
        db.session.add(trip3)
        print("✓ Created Trip 3: Tamil Nadu Divine Temple Trail")

        # Trip 4: Himalayan Adventure (adventure category)
        trip4 = Trip(
            trip_id=str(uuid.uuid4()),
            user_id=user_id,
            trip_name='Himalayan Adventure Expedition',
            trip_description='An adrenaline-pumping adventure through the majestic Himalayas - from river rafting to bungee jumping to trekking.',
            trip_category='adventure',
            cover_image='https://images.unsplash.com/photo-1593181629936-11c609b8db9b?w=800',
            start_date='2026-05-01',
            end_date='2026-05-10',
            total_budget=60000,
            is_public=True,
            itinerary_json=json.dumps({
                'stops': [
                    {
                        'city_name': 'Rishikesh',
                        'state': 'Uttarakhand',
                        'arrival_date': '2026-05-01',
                        'departure_date': '2026-05-04',
                        'image': 'https://images.unsplash.com/photo-1586439738618-1142c0cec81f?w=400',
                        'stop_category': ['adventure', 'spiritual'],
                        'days': [
                            {'day_number': 1, 'date': '2026-05-01', 'activities': [
                                {'activity_name': 'Laxman Jhula', 'time': '10:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Iconic suspension bridge'},
                                {'activity_name': 'Ram Jhula', 'time': '14:00', 'duration': '1.5 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Another famous bridge'},
                                {'activity_name': 'Ganga Aarti at Parmarth', 'time': '18:00', 'duration': '1.5 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Evening ceremony'}
                            ]},
                            {'day_number': 2, 'date': '2026-05-02', 'activities': [
                                {'activity_name': 'River Rafting', 'time': '08:00', 'duration': '4 hours', 'estimated_cost': 2000, 'category': 'adventure', 'notes': '16km Grade III-IV rapids'},
                                {'activity_name': 'Cliff Jumping', 'time': '14:00', 'duration': '2 hours', 'estimated_cost': 500, 'category': 'adventure', 'notes': 'Multiple heights'}
                            ]},
                            {'day_number': 3, 'date': '2026-05-03', 'activities': [
                                {'activity_name': 'Bungee Jumping', 'time': '09:00', 'duration': '3 hours', 'estimated_cost': 3500, 'category': 'adventure', 'notes': 'Indias highest - 83m'},
                                {'activity_name': 'Beatles Ashram', 'time': '15:00', 'duration': '2 hours', 'estimated_cost': 150, 'category': 'heritage', 'notes': 'Graffiti art'},
                                {'activity_name': 'Camping Riverside', 'time': '18:00', 'duration': '14 hours', 'estimated_cost': 2000, 'category': 'adventure', 'notes': 'Beach camping'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Shimla',
                        'state': 'Himachal Pradesh',
                        'arrival_date': '2026-05-04',
                        'departure_date': '2026-05-06',
                        'image': 'https://images.unsplash.com/photo-1597074866923-dc0589150358?w=400',
                        'stop_category': ['sightseeing', 'relaxation'],
                        'days': [
                            {'day_number': 4, 'date': '2026-05-04', 'activities': [
                                {'activity_name': 'Mall Road', 'time': '11:00', 'duration': '3 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Colonial charm'},
                                {'activity_name': 'Ridge', 'time': '15:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'City center'},
                                {'activity_name': 'Christ Church', 'time': '17:00', 'duration': '1 hour', 'estimated_cost': 0, 'category': 'heritage', 'notes': 'Neo-Gothic church'}
                            ]},
                            {'day_number': 5, 'date': '2026-05-05', 'activities': [
                                {'activity_name': 'Toy Train Ride', 'time': '09:00', 'duration': '5 hours', 'estimated_cost': 500, 'category': 'sightseeing', 'notes': 'UNESCO Heritage railway'},
                                {'activity_name': 'Jakhoo Temple', 'time': '16:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Hanuman statue, monkey point'}
                            ]}
                        ]
                    },
                    {
                        'city_name': 'Manali',
                        'state': 'Himachal Pradesh',
                        'arrival_date': '2026-05-06',
                        'departure_date': '2026-05-10',
                        'image': 'https://images.unsplash.com/photo-1593181629936-11c609b8db9b?w=400',
                        'stop_category': ['adventure', 'nature'],
                        'days': [
                            {'day_number': 6, 'date': '2026-05-06', 'activities': [
                                {'activity_name': 'Hadimba Temple', 'time': '09:00', 'duration': '1.5 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Wooden temple in cedar forest'},
                                {'activity_name': 'Old Manali Cafes', 'time': '13:00', 'duration': '3 hours', 'estimated_cost': 500, 'category': 'food', 'notes': 'Israeli cafes'},
                                {'activity_name': 'Mall Road Manali', 'time': '17:00', 'duration': '2 hours', 'estimated_cost': 0, 'category': 'shopping', 'notes': 'Tibetan market'}
                            ]},
                            {'day_number': 7, 'date': '2026-05-07', 'activities': [
                                {'activity_name': 'Solang Valley', 'time': '08:00', 'duration': '6 hours', 'estimated_cost': 3000, 'category': 'adventure', 'notes': 'Paragliding, zorbing'},
                                {'activity_name': 'Vashisht Hot Springs', 'time': '17:00', 'duration': '2 hours', 'estimated_cost': 30, 'category': 'relaxation', 'notes': 'Natural hot water'}
                            ]},
                            {'day_number': 8, 'date': '2026-05-08', 'activities': [
                                {'activity_name': 'Rohtang Pass', 'time': '06:00', 'duration': '8 hours', 'estimated_cost': 1000, 'category': 'adventure', 'notes': 'Snow activities, permit needed'},
                                {'activity_name': 'Tibetan Monastery', 'time': '18:00', 'duration': '1 hour', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Evening prayers'}
                            ]},
                            {'day_number': 9, 'date': '2026-05-09', 'activities': [
                                {'activity_name': 'River Rafting Beas', 'time': '09:00', 'duration': '3 hours', 'estimated_cost': 1500, 'category': 'adventure', 'notes': 'Grade II-III rapids'},
                                {'activity_name': 'Jogini Waterfall', 'time': '14:00', 'duration': '4 hours', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Scenic trek'},
                                {'activity_name': 'Manu Temple', 'time': '18:00', 'duration': '1 hour', 'estimated_cost': 0, 'category': 'sightseeing', 'notes': 'Ancient sage temple'}
                            ]}
                        ]
                    }
                ]
            })
        )
        db.session.add(trip4)
        print("✓ Created Trip 4: Himalayan Adventure Expedition")

        # Commit all trips
        db.session.commit()
        
        print("\n" + "="*50)
        print("Successfully created 4 trips!")
        print("="*50)
        print(f"User: {user.name} ({user.email})")
        print("-"*50)
        print("1. Royal Rajasthan Heritage Tour (heritage)")
        print("   → Jaipur → Jodhpur → Jaisalmer → Udaipur")
        print("   → Budget: ₹45,000 | Duration: 10 days")
        print()
        print("2. Kerala - Gods Own Country (nature)")
        print("   → Kochi → Alleppey → Thekkady → Munnar")
        print("   → Budget: ₹55,000 | Duration: 10 days")
        print()
        print("3. Tamil Nadu Divine Temple Trail (pilgrimage)")
        print("   → Chennai → Mahabalipuram → Thanjavur → Madurai")
        print("   → Budget: ₹35,000 | Duration: 9 days")
        print()
        print("4. Himalayan Adventure Expedition (adventure)")
        print("   → Rishikesh → Shimla → Manali")
        print("   → Budget: ₹60,000 | Duration: 10 days")
        print("="*50)


if __name__ == '__main__':
    create_sample_trips()
