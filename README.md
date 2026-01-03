# 🚀 பயணம் (Payanam) - Indian Travel Itinerary Planner

<div align="center">

![Payanam Logo](https://img.shields.io/badge/பயணம்-Payanam-EA7B7B?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDQgN3Y2YzAgNS41NSAzLjg0IDEwLjc0IDggMTIgNC4xNi0xLjI2IDgtNi40NSA4LTEyVjdMMTIgMnoiLz48L3N2Zz4=)

**Your Ultimate Indian Travel Companion**

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite)](https://sqlite.org/)

[Features](#-features) • [Installation](#-installation) • [Pages](#-pages--routes) • [API](#-api-endpoints) • [Admin](#-admin-panel)

</div>

---

## 📖 About

**Payanam** (பயணம் - meaning "Journey" in Tamil) is a comprehensive travel itinerary planning platform designed specifically for exploring the incredible diversity of India. Built for the ODOO Hackathon, it helps travelers plan, organize, and share their journeys across India's magnificent destinations.

### ✨ Key Highlights

- 🏛️ **59 Indian Cities** with detailed information
- 🎯 **590+ Activities** across all destinations  
- 📅 **Interactive Itinerary Builder** with drag-and-drop
- 💰 **Budget Tracking** and expense management
- 🔗 **Shareable Trip Links** for collaboration
- 📊 **Personal Analytics** to track travel patterns

---

## 🎯 Features

### For Travelers
| Feature | Description |
|---------|-------------|
| 🗺️ **City Explorer** | Browse 59 cities across India with images, descriptions, and activities |
| 🎪 **Activity Search** | Find activities by category, cost, duration, and city |
| 📝 **Trip Planner** | Create detailed day-by-day itineraries |
| 🔄 **Drag & Drop** | Reorder activities and days with ease |
| 💵 **Budget Tracker** | Set budgets and track expenses per trip |
| 📤 **Share Trips** | Generate public links to share itineraries |
| 📈 **Analytics** | View travel statistics and patterns |

### For Admins
| Feature | Description |
|---------|-------------|
| 👥 **User Management** | View and manage registered users |
| ✈️ **Trip Overview** | Monitor all trips on the platform |
| 🏙️ **City Database** | Add, edit, and remove cities |
| 🎯 **Activity Database** | Manage activities across all cities |
| 📊 **Platform Analytics** | View platform-wide statistics |

---

## 🛠️ Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/payanam.git
cd payanam

# 2. Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

### Environment Setup

Create a `.env` file in the root directory:

```env
# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin

# Flask Settings (optional)
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
```

---

## 🌐 Pages & Routes

### 🔓 Public Pages (No Login Required)

| Page | URL | Description |
|------|-----|-------------|
| 🏠 **Home** | `/` | Landing page with features and CTA |
| 🔐 **Login** | `/login` | User authentication page |
| 📝 **Sign Up** | `/signup` | New user registration |
| 🔗 **Shared Trip** | `/shared/<share_id>` | View publicly shared trips |

### 🔒 Protected Pages (Login Required)

| Page | URL | Description |
|------|-----|-------------|
| 📊 **Dashboard** | `/dashboard` | User's personal dashboard with quick stats |
| ✈️ **My Trips** | `/trips` | List of all user's trips |
| ➕ **Create Trip** | `/trip/create` | Create a new trip |
| 👁️ **View Trip** | `/trip/<trip_id>` | View trip details and itinerary |
| ✏️ **Edit Trip** | `/trip/<trip_id>/edit` | Edit existing trip |
| 🏗️ **Itinerary Builder** | `/trip/<trip_id>/itinerary` | Build day-by-day itinerary |
| ⏱️ **Timeline View** | `/trip/<trip_id>/timeline` | Visual timeline of the trip |
| 💰 **Budget Tracker** | `/trip/<trip_id>/budget` | Manage trip budget and expenses |
| 🏙️ **City Search** | `/cities` | Browse and search all cities |
| 🎯 **Activity Search** | `/activities` | Search activities across cities |
| 👤 **Profile** | `/profile` | User profile and settings |
| 📈 **Analytics** | `/analytics` | Personal travel analytics |
| 🚪 **Logout** | `/logout` | End user session |

### 🔐 Admin Pages

| Page | URL | Description |
|------|-----|-------------|
| 🔑 **Admin Login** | `/admin/login` | Admin authentication |
| 📋 **Admin Dashboard** | `/admin` | Full admin panel with all management features |
| 🚪 **Admin Logout** | `/admin/logout` | End admin session |

---

## 🔌 API Endpoints

### Public APIs

```
GET  /api/cities              # Get all cities
GET  /api/cities/<city_id>    # Get city details
GET  /api/activities          # Get all activities
GET  /api/activities/search   # Search activities with filters
```

### Protected APIs (Require Login)

```
GET  /api/trips               # Get user's trips
POST /api/trips               # Create new trip
GET  /api/trips/<trip_id>     # Get trip details
PUT  /api/trips/<trip_id>     # Update trip
DELETE /api/trips/<trip_id>   # Delete trip

POST /api/profile/update      # Update user profile
POST /profile/delete          # Delete user account
```

### Admin APIs

```
DELETE /admin/api/user/<user_id>         # Delete user
DELETE /admin/api/trip/<trip_id>         # Delete trip
DELETE /admin/api/city/<city_id>         # Delete city
DELETE /admin/api/activity/<activity_id> # Delete activity
POST   /admin/city                       # Add new city
POST   /admin/activity                   # Add new activity
```

---

## 👤 User Guide

### Creating Your First Trip

1. **Sign Up / Login** at `/signup` or `/login`
2. Navigate to **Dashboard** → Click **"Create New Trip"**
3. Fill in trip details:
   - Trip name
   - Category (Heritage, Nature, Adventure, etc.)
   - Start and end dates
   - Budget
4. Click **"Create Trip"**
5. Use the **Itinerary Builder** to add cities and activities

### Building an Itinerary

1. Open your trip → Click **"Build Itinerary"**
2. **Add a Stop**: Search and select a city
3. **Add Activities**: Browse available activities or search
4. **Organize**: Drag and drop to reorder
5. **Set Times**: Assign time slots to each activity
6. **Save**: Your itinerary auto-saves

### Sharing Your Trip

1. Open the trip you want to share
2. Click **"Share Trip"** button
3. Toggle **"Make Public"** option
4. Copy the generated share link
5. Anyone with the link can view your itinerary

---

## 🔐 Admin Panel

### Accessing Admin

1. Navigate to `/admin/login`
2. Enter credentials:
   - **Username**: `admin`
   - **Password**: `admin`
3. You'll be redirected to the admin dashboard

### Admin Features

#### 📊 Dashboard Overview
- Total users, trips, cities, and activities
- Platform insights and analytics
- Quick access to all management sections

#### 👥 Users Tab
- View all registered users
- See user details (name, email, trip count)
- Delete users (cascades to their trips)

#### ✈️ Trips Tab
- View all trips on the platform
- Filter by category, date, or user
- Quick view and delete options

#### 🏙️ Cities Tab
- View all 59 cities with images
- Search cities by name or state
- Add new cities
- Delete cities (cascades to activities)

#### 🎯 Activities Tab
- View all 590+ activities
- See activity details (city, duration, cost, rating)
- Add new activities
- Delete activities

#### 📈 Analytics Tab
- Monthly trip trends
- Budget distribution analysis
- Category popularity
- Recent platform activity

---

## 📁 Project Structure

```
Travel-Planner/
├── 📄 app.py                 # Main Flask application
├── 📄 models.py              # SQLAlchemy database models
├── 📄 add_trips.py           # Sample data seeder
├── 📄 requirements.txt       # Python dependencies
├── 📄 .env                   # Environment variables
├── 📄 README.md              # This file
│
├── 📁 instance/
│   └── 📄 payanam.db         # SQLite database
│
└── 📁 templates/
    ├── 📄 base.html          # Base template with navbar/footer
    ├── 📄 index.html         # Home page
    ├── 📄 login.html         # Login page
    ├── 📄 signup.html        # Registration page
    ├── 📄 dashboard.html     # User dashboard
    ├── 📄 my_trips.html      # Trip listing
    ├── 📄 create_trip.html   # Trip creation form
    ├── 📄 view_trip.html     # Trip details view
    ├── 📄 edit_trip.html     # Trip editing form
    ├── 📄 itinerary_builder.html  # Itinerary builder
    ├── 📄 timeline.html      # Timeline view
    ├── 📄 budget.html        # Budget tracker
    ├── 📄 city_search.html   # City explorer
    ├── 📄 activity_search.html    # Activity search
    ├── 📄 profile.html       # User profile
    ├── 📄 analytics.html     # User analytics
    ├── 📄 shared_trip.html   # Public shared trip view
    ├── 📄 admin_login.html   # Admin login
    └── 📄 admin.html         # Admin dashboard
```

---

## 🗄️ Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| user_id | String(36) | Primary key (UUID) |
| name | String(100) | User's display name |
| email | String(150) | Unique email address |
| avatar_url | String(500) | Profile picture URL |
| language_pref | String(10) | Preferred language |
| created_at | DateTime | Registration timestamp |

### Trips Table
| Column | Type | Description |
|--------|------|-------------|
| trip_id | String(36) | Primary key (UUID) |
| user_id | String(36) | Foreign key to users |
| trip_name | String(200) | Trip title |
| trip_description | Text | Trip description |
| trip_category | String(50) | Category (heritage, nature, etc.) |
| cover_image | String(500) | Cover image URL |
| start_date | String(20) | Trip start date |
| end_date | String(20) | Trip end date |
| total_budget | Float | Total budget in INR |
| is_public | Boolean | Public visibility flag |
| share_id | String(36) | Unique share identifier |
| itinerary_json | Text | JSON itinerary data |
| created_at | DateTime | Creation timestamp |

### Cities Table
| Column | Type | Description |
|--------|------|-------------|
| city_id | String(36) | Primary key (UUID) |
| name | String(100) | City name |
| state | String(100) | State name |
| description | Text | City description |
| image_url | String(500) | City image URL |
| category | String(50) | Primary category |
| popular_score | Integer | Popularity ranking |
| avg_cost_per_day | Float | Average daily cost |
| best_time_to_visit | String(100) | Best season to visit |

### Activities Table
| Column | Type | Description |
|--------|------|-------------|
| activity_id | String(36) | Primary key (UUID) |
| city_id | String(36) | Foreign key to cities |
| name | String(200) | Activity name |
| description | Text | Activity description |
| category | String(50) | Activity category |
| estimated_cost | Float | Cost in INR |
| duration_hours | Float | Duration in hours |
| image_url | String(500) | Activity image URL |
| rating | Float | Average rating (1-5) |
| tips | Text | Travel tips |

---

## 🎨 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Flask 3.1.2** | Backend web framework |
| **SQLAlchemy** | ORM for database operations |
| **SQLite** | Database storage |
| **TailwindCSS** | Utility-first CSS framework |
| **Bootstrap 5** | UI components |
| **Font Awesome** | Icons |
| **AOS** | Scroll animations |
| **Vanilla JS** | Frontend interactivity |

---

## 📊 Sample Data

The application comes pre-loaded with:

- **59 Cities** across India including:
  - Rajasthan: Jaipur, Jodhpur, Udaipur, Jaisalmer
  - Kerala: Kochi, Munnar, Alleppey, Thekkady
  - Tamil Nadu: Chennai, Madurai, Thanjavur
  - Himalayas: Shimla, Manali, Rishikesh
  - And many more...

- **590+ Activities** covering:
  - 🏛️ Heritage & Monuments
  - 🛕 Temples & Spiritual
  - 🏔️ Adventure & Trekking
  - 🌿 Nature & Wildlife
  - 🍽️ Food & Cuisine
  - 🛍️ Shopping & Markets

---

## 🚀 Deployment

### Local Development
```bash
python app.py
# Server runs at http://127.0.0.1:5000
```

### Production (Example with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📝 Sample User Credentials

For testing purposes, you can create an account or use:

| Type | Email | Password |
|------|-------|----------|
| Regular User | *(Create via signup)* | *(Your choice)* |
| Admin | admin | admin |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is built for the **ODOO Hackathon 2026**.

---

## 👨‍💻 Author

**Manikandan K S**
- Email: mani.ks1324579@gmail.com
- Project: Payanam - Indian Travel Itinerary Planner

---

<div align="center">

### 🙏 நன்றி (Thank You)

**Happy Traveling with பயணம்!** 🇮🇳

</div>
