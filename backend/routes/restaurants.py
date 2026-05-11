from flask import request, jsonify
import jwt
from datetime import datetime
from database import db
from models import Restaurant, User, MenuItem
from routes.auth import get_user_from_token

def get_user_from_token():
    """Extract and validate user from JWT token"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None, 'Missing or invalid authorization header'
    
    try:
        from config import Config
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'

def register_routes(bp):
    """Register restaurant routes"""
    
    @bp.route('', methods=['GET'])
    def get_restaurants():
        """Get all restaurants with optional filters"""
        try:
            # Get query parameters
            cuisine = request.args.get('cuisine', '')
            search = request.args.get('search', '')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # Build query
            query = Restaurant.query.filter_by(is_active=True)
            
            if cuisine:
                query = query.filter_by(cuisine=cuisine)
            
            if search:
                query = query.filter(
                    (Restaurant.name.ilike(f'%{search}%')) |
                    (Restaurant.location.ilike(f'%{search}%'))
                )
            
            # Paginate
            paginated = query.paginate(page=page, per_page=per_page)
            
            restaurants = [{
                'id': r.id,
                'name': r.name,
                'cuisine': r.cuisine,
                'location': r.location,
                'rating': r.rating,
                'is_active': r.is_active,
                'phone': r.phone,
                'hours_open': r.hours_open
            } for r in paginated.items]
            
            return jsonify({
                'restaurants': restaurants,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }), 200
        except Exception as e:
            return jsonify({'message': f'Error fetching restaurants: {str(e)}'}), 500
    
    @bp.route('/<int:restaurant_id>', methods=['GET'])
    def get_restaurant(restaurant_id):
        """Get restaurant details"""
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            
            if not restaurant:
                return jsonify({'message': 'Restaurant not found'}), 404
            
            menu_items = [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category': item.category,
                'is_available': item.is_available,
                'preparation_time': item.preparation_time
            } for item in restaurant.menu_items]
            
            return jsonify({
                'id': restaurant.id,
                'name': restaurant.name,
                'cuisine': restaurant.cuisine,
                'location': restaurant.location,
                'rating': restaurant.rating,
                'phone': restaurant.phone,
                'hours_open': restaurant.hours_open,
                'owner_id': restaurant.owner_id,
                'menu_items': menu_items
            }), 200
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    @bp.route('', methods=['POST'])
    def create_restaurant():
        """Create a new restaurant (RestaurantOwner only)"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        # Check if user has RestaurantOwner role
        if 'RestaurantOwner' not in payload.get('roles', []):
            return jsonify({'message': 'Only RestaurantOwners can create restaurants'}), 403
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ['name', 'cuisine', 'location']):
            return jsonify({'message': 'Name, cuisine, and location are required'}), 400
        
        try:
            restaurant = Restaurant(
                name=data['name'],
                cuisine=data['cuisine'],
                location=data['location'],
                owner_id=payload['user_id'],
                phone=data.get('phone', ''),
                hours_open=data.get('hours_open', ''),
                is_active=True
            )
            
            db.session.add(restaurant)
            db.session.commit()
            
            return jsonify({
                'message': 'Restaurant created successfully',
                'id': restaurant.id,
                'name': restaurant.name
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error creating restaurant: {str(e)}'}), 500
    
    @bp.route('/<int:restaurant_id>', methods=['PUT'])
    def update_restaurant(restaurant_id):
        """Update restaurant details"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            
            if not restaurant:
                return jsonify({'message': 'Restaurant not found'}), 404
            
            # Check ownership or admin role
            if restaurant.owner_id != payload['user_id'] and 'Admin' not in payload.get('roles', []):
                return jsonify({'message': 'Unauthorized'}), 403
            
            data = request.get_json()
            
            # Update fields
            if 'name' in data:
                restaurant.name = data['name']
            if 'cuisine' in data:
                restaurant.cuisine = data['cuisine']
            if 'location' in data:
                restaurant.location = data['location']
            if 'phone' in data:
                restaurant.phone = data['phone']
            if 'hours_open' in data:
                restaurant.hours_open = data['hours_open']
            if 'is_active' in data:
                restaurant.is_active = data['is_active']
            
            restaurant.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'Restaurant updated successfully',
                'id': restaurant.id,
                'name': restaurant.name
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error updating restaurant: {str(e)}'}), 500
    
    @bp.route('/<int:restaurant_id>', methods=['DELETE'])
    def delete_restaurant(restaurant_id):
        """Delete restaurant"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            
            if not restaurant:
                return jsonify({'message': 'Restaurant not found'}), 404
            
            # Check ownership or admin role
            if restaurant.owner_id != payload['user_id'] and 'Admin' not in payload.get('roles', []):
                return jsonify({'message': 'Unauthorized'}), 403
            
            db.session.delete(restaurant)
            db.session.commit()
            
            return jsonify({'message': 'Restaurant deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error deleting restaurant: {str(e)}'}), 500
    
    @bp.route('/<int:restaurant_id>/menu', methods=['GET'])
    def get_restaurant_menu(restaurant_id):
        """Get restaurant menu items"""
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            
            if not restaurant:
                return jsonify({'message': 'Restaurant not found'}), 404
            
            category = request.args.get('category', '')
            
            query = restaurant.menu_items
            if category:
                query = [item for item in query if item.category == category]
            
            menu_items = [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category': item.category,
                'is_available': item.is_available,
                'preparation_time': item.preparation_time
            } for item in query]
            
            return jsonify({'menu_items': menu_items}), 200
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    @bp.route('/<int:restaurant_id>/menu', methods=['POST'])
    def add_menu_item(restaurant_id):
        """Add menu item to restaurant"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        try:
            restaurant = Restaurant.query.get(restaurant_id)
            
            if not restaurant:
                return jsonify({'message': 'Restaurant not found'}), 404
            
            # Check ownership or admin role
            if restaurant.owner_id != payload['user_id'] and 'Admin' not in payload.get('roles', []):
                return jsonify({'message': 'Unauthorized'}), 403
            
            data = request.get_json()
            
            if not all(k in data for k in ['name', 'price', 'category']):
                return jsonify({'message': 'Name, price, and category are required'}), 400
            
            menu_item = MenuItem(
                name=data['name'],
                description=data.get('description', ''),
                price=data['price'],
                category=data['category'],
                restaurant_id=restaurant_id,
                is_available=data.get('is_available', True),
                preparation_time=data.get('preparation_time', 30)
            )
            
            db.session.add(menu_item)
            db.session.commit()
            
            return jsonify({
                'message': 'Menu item added successfully',
                'id': menu_item.id,
                'name': menu_item.name
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error adding menu item: {str(e)}'}), 500
