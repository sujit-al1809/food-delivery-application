from flask import request, jsonify
import jwt
from datetime import datetime
from database import db
from models import Order, OrderItem, MenuItem, User
from tasks import send_order_status_email

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
    """Register order routes"""
    
    @bp.route('', methods=['POST'])
    def create_order():
        """Create a new order"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        data = request.get_json()
        
        if not data or 'restaurant_id' not in data or 'items' not in data:
            return jsonify({'message': 'restaurant_id and items are required'}), 400
        
        try:
            # Calculate total price and validate items
            total_price = 0
            order_items_data = []
            
            for item_data in data['items']:
                menu_item = MenuItem.query.get(item_data['menuitem_id'])
                
                if not menu_item:
                    return jsonify({'message': f'Menu item {item_data["menuitem_id"]} not found'}), 404
                
                if not menu_item.is_available:
                    return jsonify({'message': f'{menu_item.name} is not available'}), 400
                
                quantity = item_data.get('quantity', 1)
                item_total = menu_item.price * quantity
                total_price += item_total
                
                order_items_data.append({
                    'menu_item': menu_item,
                    'quantity': quantity,
                    'price': menu_item.price
                })
            
            # Create order
            order = Order(
                user_id=payload['user_id'],
                restaurant_id=data['restaurant_id'],
                total_price=total_price,
                delivery_address=data.get('delivery_address', ''),
                special_instructions=data.get('special_instructions', ''),
                status='Pending'
            )
            
            db.session.add(order)
            db.session.flush()  # Get order ID before committing
            
            # Add order items
            for item_info in order_items_data:
                order_item = OrderItem(
                    order_id=order.id,
                    menuitem_id=item_info['menu_item'].id,
                    quantity=item_info['quantity'],
                    price=item_info['price'],
                    special_instructions=item_info.get('special_instructions', '')
                )
                db.session.add(order_item)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Order created successfully',
                'order_id': order.id,
                'total_price': total_price,
                'status': order.status
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error creating order: {str(e)}'}), 500
    
    @bp.route('/<int:order_id>', methods=['GET'])
    def get_order(order_id):
        """Get order details"""
        try:
            order = Order.query.get(order_id)
            
            if not order:
                return jsonify({'message': 'Order not found'}), 404
            
            items = [{
                'id': item.id,
                'menuitem_id': item.menuitem_id,
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'price': item.price,
                'subtotal': item.quantity * item.price
            } for item in order.items]
            
            return jsonify({
                'id': order.id,
                'user_id': order.user_id,
                'restaurant_id': order.restaurant_id,
                'restaurant_name': order.restaurant.name,
                'items': items,
                'total_price': order.total_price,
                'status': order.status,
                'delivery_address': order.delivery_address,
                'special_instructions': order.special_instructions,
                'estimated_delivery_time': order.estimated_delivery_time,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            }), 200
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    @bp.route('/<int:order_id>/status', methods=['PUT'])
    def update_order_status(order_id):
        """Update order status"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({'message': 'status is required'}), 400
        
        try:
            order = Order.query.get(order_id)
            
            if not order:
                return jsonify({'message': 'Order not found'}), 404
            
            # Check authorization (admin, restaurant owner, or delivery agent)
            user_roles = payload.get('roles', [])
            is_authorized = (
                'Admin' in user_roles or
                order.restaurant.owner_id == payload['user_id'] or
                'DeliveryAgent' in user_roles
            )
            
            if not is_authorized:
                return jsonify({'message': 'Unauthorized'}), 403
            
            new_status = data['status']
            old_status = order.status
            
            # Valid status transitions
            valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered', 'Cancelled']
            
            if new_status not in valid_statuses:
                return jsonify({'message': f'Invalid status: {new_status}'}), 400
            
            order.status = new_status
            order.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Trigger Celery task if status changed to "Out for Delivery"
            if new_status == 'Out for Delivery' and old_status != 'Out for Delivery':
                send_order_status_email.delay(order.id)
            
            return jsonify({
                'message': 'Order status updated successfully',
                'order_id': order.id,
                'status': order.status
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error updating order: {str(e)}'}), 500
    
    @bp.route('/user/my-orders', methods=['GET'])
    def get_user_orders():
        """Get current user's orders"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            status = request.args.get('status', '')
            
            query = Order.query.filter_by(user_id=payload['user_id'])
            
            if status:
                query = query.filter_by(status=status)
            
            # Sort by most recent first
            query = query.order_by(Order.created_at.desc())
            
            paginated = query.paginate(page=page, per_page=per_page)
            
            orders = [{
                'id': order.id,
                'restaurant_name': order.restaurant.name,
                'total_price': order.total_price,
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'estimated_delivery_time': order.estimated_delivery_time
            } for order in paginated.items]
            
            return jsonify({
                'orders': orders,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }), 200
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    @bp.route('', methods=['GET'])
    def get_all_orders():
        """Get all orders (Admin or RestaurantOwner)"""
        payload, error = get_user_from_token()
        
        if error:
            return jsonify({'message': error}), 401
        
        user_roles = payload.get('roles', [])
        
        if 'Admin' not in user_roles and 'RestaurantOwner' not in user_roles:
            return jsonify({'message': 'Unauthorized'}), 403
        
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            status = request.args.get('status', '')
            restaurant_id = request.args.get('restaurant_id', type=int)
            
            query = Order.query
            
            # RestaurantOwners can only see their restaurant's orders
            if 'RestaurantOwner' in user_roles and 'Admin' not in user_roles:
                from models import Restaurant
                user_restaurants = Restaurant.query.filter_by(owner_id=payload['user_id']).all()
                restaurant_ids = [r.id for r in user_restaurants]
                query = query.filter(Order.restaurant_id.in_(restaurant_ids))
            elif restaurant_id:
                query = query.filter_by(restaurant_id=restaurant_id)
            
            if status:
                query = query.filter_by(status=status)
            
            paginated = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page)
            
            orders = [{
                'id': order.id,
                'customer_email': order.customer.email,
                'restaurant_name': order.restaurant.name,
                'total_price': order.total_price,
                'status': order.status,
                'created_at': order.created_at.isoformat()
            } for order in paginated.items]
            
            return jsonify({
                'orders': orders,
                'total': paginated.total,
                'pages': paginated.pages,
                'current_page': page
            }), 200
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
