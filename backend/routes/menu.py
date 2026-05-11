from flask import request, jsonify
import jwt
from datetime import datetime
from database import db
from models import MenuItem, Restaurant

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
    """Register menu item routes"""
    
    @bp.route('/<int:menu_id>', methods=['GET'])
    def get_menu_item(menu_id):
        """Get menu item details"""
        try:
            item = MenuItem.query.get(menu_id)
            
            if not item:
                return jsonify({'message': 'Menu item not found'}), 404
            
            return jsonify({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category': item.category,
                'restaurant_id': item.restaurant_id,
                'is_available': item.is_available,
                'preparation_time': item.preparation_time,
                'image_url': item.image_url
            }), 200
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    @bp.route('/<int:menu_id>', methods=['PUT'])
    def update_menu_item(menu_id):
        """Update menu item"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        try:
            item = MenuItem.query.get(menu_id)
            
            if not item:
                return jsonify({'message': 'Menu item not found'}), 404
            
            restaurant = item.restaurant
            
            # Check ownership or admin role
            if restaurant.owner_id != payload['user_id'] and 'Admin' not in payload.get('roles', []):
                return jsonify({'message': 'Unauthorized'}), 403
            
            data = request.get_json()
            
            # Update fields
            if 'name' in data:
                item.name = data['name']
            if 'description' in data:
                item.description = data['description']
            if 'price' in data:
                item.price = data['price']
            if 'category' in data:
                item.category = data['category']
            if 'is_available' in data:
                item.is_available = data['is_available']
            if 'preparation_time' in data:
                item.preparation_time = data['preparation_time']
            if 'image_url' in data:
                item.image_url = data['image_url']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Menu item updated successfully',
                'id': item.id,
                'name': item.name
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error updating menu item: {str(e)}'}), 500
    
    @bp.route('/<int:menu_id>', methods=['DELETE'])
    def delete_menu_item(menu_id):
        """Delete menu item"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        try:
            item = MenuItem.query.get(menu_id)
            
            if not item:
                return jsonify({'message': 'Menu item not found'}), 404
            
            restaurant = item.restaurant
            
            # Check ownership or admin role
            if restaurant.owner_id != payload['user_id'] and 'Admin' not in payload.get('roles', []):
                return jsonify({'message': 'Unauthorized'}), 403
            
            db.session.delete(item)
            db.session.commit()
            
            return jsonify({'message': 'Menu item deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error deleting menu item: {str(e)}'}), 500
    
    @bp.route('/search', methods=['GET'])
    def search_menu_items():
        """Search menu items across all restaurants"""
        try:
            search_query = request.args.get('q', '')
            cuisine = request.args.get('cuisine', '')
            category = request.args.get('category', '')
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # Build query
            query = MenuItem.query.filter(MenuItem.restaurant.has(is_active=True))
            
            if search_query:
                query = query.filter(MenuItem.name.ilike(f'%{search_query}%'))
            
            if cuisine:
                query = query.filter(MenuItem.restaurant.has(cuisine=cuisine))
            
            if category:
                query = query.filter_by(category=category)
            
            if min_price is not None:
                query = query.filter(MenuItem.price >= min_price)
            
            if max_price is not None:
                query = query.filter(MenuItem.price <= max_price)
            
            # Paginate
            paginated = query.paginate(page=page, per_page=per_page)
            
            items = [{
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
                'category': item.category,
                'restaurant_id': item.restaurant_id,
                'restaurant_name': item.restaurant.name,
                'is_available': item.is_available,
                'preparation_time': item.preparation_time
            } for item in paginated.items]
            
            return jsonify({
                'items': items,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }), 200
        except Exception as e:
            return jsonify({'message': f'Error searching menu items: {str(e)}'}), 500
