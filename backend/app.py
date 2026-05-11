"""
Food Delivery Application
Full-stack web application for food delivery service

Backend: Flask, SQLAlchemy
Frontend: Vue.js
Features: Authentication, Restaurant Management, Order Management, ETA Prediction, Email Notifications
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from config import config
from database import db, init_db
from models import User, Role
from tasks import init_celery
from flask_security.utils import hash_password
import uuid

# Load environment variables
load_dotenv()

def create_app(config_name=None):
    """Factory function to create and configure Flask app"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize Celery
    celery = init_celery(app)
    app.celery = celery
    
    # Initialize database
    with app.app_context():
        init_db(app)
        create_default_roles()
        create_default_admin()
    
    # Register blueprints
    from routes import create_routes
    create_routes(app)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'Food Delivery API'}), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'message': 'Internal server error'}), 500
    
    return app

def create_default_roles():
    """Create default roles if they don't exist"""
    try:
        from database import db
        
        roles_to_create = [
            ('Customer', 'Regular customer'),
            ('RestaurantOwner', 'Restaurant owner'),
            ('DeliveryAgent', 'Delivery agent'),
            ('Admin', 'Administrator')
        ]
        
        for role_name, description in roles_to_create:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name, description=description)
                db.session.add(role)
        
        db.session.commit()
        print("Default roles created/verified")
    except Exception as e:
        print(f"Error creating roles: {e}")
        db.session.rollback()

def create_default_admin():
    """Create default admin user if it doesn't exist"""
    try:
        from database import db
        
        admin_email = 'admin@fooddelivery.com'
        admin_password = 'admin123456'
        
        if not User.query.filter_by(email=admin_email).first():
            admin_role = Role.query.filter_by(name='Admin').first()
            
            admin = User(
                email=admin_email,
                password=hash_password(admin_password),
                fs_uniquifier=str(uuid.uuid4()),
                first_name='Admin',
                last_name='User',
                active=True
            )
            admin.roles.append(admin_role)
            db.session.add(admin)
            db.session.commit()
            print(f"Default admin user created: {admin_email}")
        else:
            print("Admin user already exists")
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.session.rollback()

# CLI Commands for management
@staticmethod
def register_cli(app):
    """Register CLI commands"""
    
    @app.cli.command()
    def init_db_command():
        """Initialize the database"""
        init_db(app)
        print("Database initialized")
    
    @app.cli.command()
    def train_model():
        """Train the ML model for ETA prediction"""
        from train_model import train_model as train_eta_model
        train_eta_model()
    
    @app.cli.command()
    def create_sample_data():
        """Create sample restaurants and menu items"""
        from models import Restaurant, MenuItem
        
        with app.app_context():
            try:
                # Find a restaurant owner
                owner = User.query.join(User.roles).filter(Role.name == 'RestaurantOwner').first()
                
                if not owner:
                    print("No RestaurantOwner found. Create one first.")
                    return
                
                # Create sample restaurants
                restaurants_data = [
                    {
                        'name': 'The Pizza Palace',
                        'cuisine': 'Italian',
                        'location': '123 Main St',
                        'phone': '555-0101',
                        'hours_open': '11AM-11PM',
                        'menu': [
                            {'name': 'Margherita Pizza', 'price': 12.99, 'category': 'Pizza', 'prep_time': 15},
                            {'name': 'Caesar Salad', 'price': 8.99, 'category': 'Salad', 'prep_time': 5},
                            {'name': 'Tiramisu', 'price': 6.99, 'category': 'Dessert', 'prep_time': 2},
                        ]
                    },
                    {
                        'name': 'Burger Barn',
                        'cuisine': 'American',
                        'location': '456 Oak Ave',
                        'phone': '555-0102',
                        'hours_open': '10AM-10PM',
                        'menu': [
                            {'name': 'Classic Burger', 'price': 10.99, 'category': 'Burger', 'prep_time': 12},
                            {'name': 'Fries', 'price': 3.99, 'category': 'Sides', 'prep_time': 8},
                            {'name': 'Milkshake', 'price': 5.99, 'category': 'Drinks', 'prep_time': 5},
                        ]
                    }
                ]
                
                for rest_data in restaurants_data:
                    menu_data = rest_data.pop('menu')
                    
                    restaurant = Restaurant(
                        **rest_data,
                        owner_id=owner.id,
                        is_active=True
                    )
                    db.session.add(restaurant)
                    db.session.flush()
                    
                    for item_data in menu_data:
                        menu_item = MenuItem(
                            **item_data,
                            restaurant_id=restaurant.id,
                            is_available=True,
                            preparation_time=item_data.pop('prep_time')
                        )
                        db.session.add(menu_item)
                
                db.session.commit()
                print("Sample data created successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating sample data: {e}")

if __name__ == '__main__':
    app = create_app()
    register_cli(app)
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
