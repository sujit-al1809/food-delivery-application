from celery import Celery
import os
from datetime import datetime

# Initialize Celery
celery_app = Celery(__name__)

def init_celery(app):
    """Initialize Celery with Flask app"""
    celery_app.conf.update(app.config)
    
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task = ContextTask
    return celery_app

@celery_app.task
def send_order_status_email(order_id):
    """Send email notification when order status changes to 'Out for Delivery'"""
    from database import db
    from models import Order
    
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return {'status': 'error', 'message': f'Order {order_id} not found'}
        
        customer = order.customer
        restaurant = order.restaurant
        
        # Email subject and body
        subject = f"Your order from {restaurant.name} is out for delivery!"
        
        body = f"""
        Dear {customer.first_name},
        
        Good news! Your order from {restaurant.name} is on its way.
        
        Order Details:
        - Order ID: {order.id}
        - Restaurant: {restaurant.name}
        - Delivery Address: {order.delivery_address}
        - Estimated Delivery Time: {order.estimated_delivery_time} minutes
        - Total Amount: ${order.total_price:.2f}
        
        Items:
        """
        
        for item in order.items:
            body += f"\n- {item.menu_item.name} x{item.quantity}: ${item.price * item.quantity:.2f}"
        
        body += """
        
        Thank you for ordering with us!
        
        Best regards,
        Food Delivery Team
        """
        
        # In production, use Flask-Mail or similar to send actual emails
        # For now, we'll just log it
        print(f"[EMAIL] To: {customer.email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body:\n{body}")
        
        return {
            'status': 'success',
            'message': f'Email sent for order {order_id}',
            'email': customer.email
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def send_order_confirmation_email(order_id):
    """Send email confirmation when order is placed"""
    from models import Order
    
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return {'status': 'error', 'message': f'Order {order_id} not found'}
        
        customer = order.customer
        restaurant = order.restaurant
        
        subject = f"Order Confirmation - {restaurant.name}"
        
        body = f"""
        Dear {customer.first_name},
        
        Thank you for your order! We've received it and are preparing your food.
        
        Order Details:
        - Order ID: {order.id}
        - Restaurant: {restaurant.name}
        - Delivery Address: {order.delivery_address}
        - Total Amount: ${order.total_price:.2f}
        
        Items Ordered:
        """
        
        for item in order.items:
            body += f"\n- {item.menu_item.name} x{item.quantity}: ${item.price * item.quantity:.2f}"
        
        body += f"""
        
        Your order status: {order.status}
        
        You can track your order in the app.
        
        Best regards,
        Food Delivery Team
        """
        
        print(f"[EMAIL] To: {customer.email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body:\n{body}")
        
        return {
            'status': 'success',
            'message': f'Confirmation email sent for order {order_id}',
            'email': customer.email
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def cleanup_old_orders(days=90):
    """Cleanup old cancelled/delivered orders (optional maintenance task)"""
    from datetime import timedelta
    from models import Order
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = Order.query.filter(
            Order.created_at < cutoff_date,
            Order.status.in_(['Delivered', 'Cancelled'])
        ).delete()
        
        db.session.commit()
        
        return {
            'status': 'success',
            'message': f'Deleted {deleted_count} old orders'
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
