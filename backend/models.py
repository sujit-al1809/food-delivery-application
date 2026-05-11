from datetime import datetime
from database import db
from flask_security import UserMixin, RoleMixin

# Association table for User roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    """Role model for Flask-Security"""
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model, UserMixin):
    """User model"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    
    # Profile info
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Foreign keys for specific roles
    owned_restaurants = db.relationship('Restaurant', backref='owner', lazy=True, foreign_keys='Restaurant.owner_id')
    orders = db.relationship('Order', backref='customer', lazy=True, foreign_keys='Order.user_id')
    delivery_profile = db.relationship('DeliveryAgent', backref='user', uselist=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Restaurant(db.Model):
    """Restaurant model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    cuisine = db.Column(db.String(100), nullable=False)
    location = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Float, default=5.0)
    is_active = db.Column(db.Boolean, default=True)
    phone = db.Column(db.String(20))
    hours_open = db.Column(db.String(50))  # e.g., "9AM-11PM"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu_items = db.relationship('MenuItem', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='restaurant', lazy=True)
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'

class MenuItem(db.Model):
    """Menu Item model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # e.g., "Appetizer", "Main", "Dessert"
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500))
    preparation_time = db.Column(db.Integer)  # in minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='menu_item', lazy=True)
    
    def __repr__(self):
        return f'<MenuItem {self.name}>'

class Order(db.Model):
    """Order model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Confirmed, Preparing, Out for Delivery, Delivered, Cancelled
    delivery_address = db.Column(db.Text, nullable=False)
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    estimated_delivery_time = db.Column(db.Integer)  # in minutes, predicted by AI
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    """Order Item model (junction between Order and MenuItem)"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menuitem_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)  # Price at time of order
    special_instructions = db.Column(db.Text)
    
    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Item:{self.menuitem_id}>'

class DeliveryAgent(db.Model):
    """Delivery Agent model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    current_location = db.Column(db.String(500))  # Store as coordinates or address
    vehicle_type = db.Column(db.String(50))  # e.g., "Bike", "Car"
    license_plate = db.Column(db.String(20))
    rating = db.Column(db.Float, default=5.0)
    total_deliveries = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeliveryAgent {self.user_id}>'
