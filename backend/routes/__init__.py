from flask import Blueprint

def create_routes(app):
    """Register all route blueprints"""
    from . import auth, restaurants, menu, orders, prediction
    
    # Create blueprints
    auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
    restaurants_bp = Blueprint('restaurants', __name__, url_prefix='/api/restaurants')
    menu_bp = Blueprint('menu', __name__, url_prefix='/api/menu')
    orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')
    prediction_bp = Blueprint('prediction', __name__, url_prefix='/api')
    
    # Register route handlers
    auth.register_routes(auth_bp)
    restaurants.register_routes(restaurants_bp)
    menu.register_routes(menu_bp)
    orders.register_routes(orders_bp)
    prediction.register_routes(prediction_bp)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(restaurants_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(prediction_bp)
