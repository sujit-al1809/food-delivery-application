from flask import request, jsonify
from flask_security.utils import hash_password, verify_password
from flask_security import current_user, auth_required, roles_required
import jwt
import uuid
from datetime import datetime, timedelta
from database import db
from models import User, Role

def register_routes(bp):
    """Register authentication routes"""
    
    @bp.route('/register', methods=['POST'])
    def register():
        """Register a new user"""
        data = request.get_json()
        
        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        role_name = data.get('role', 'Customer')
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 409
        
        try:
            # Get role
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                return jsonify({'message': f'Role {role_name} does not exist'}), 400
            
            # Create user
            user = User(
                email=data['email'],
                password=hash_password(data['password']),
                fs_uniquifier=str(uuid.uuid4()),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                phone=data.get('phone', ''),
                active=True
            )
            user.roles.append(role)
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'User registered successfully',
                'user_id': user.id,
                'email': user.email,
                'role': role_name
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Registration failed: {str(e)}'}), 500
    
    @bp.route('/login', methods=['POST'])
    def login():
        """Login user and return JWT token"""
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        try:
            user = User.query.filter_by(email=data['email']).first()
            
            if not user or not verify_password(data['password'], user.password):
                return jsonify({'message': 'Invalid email or password'}), 401
            
            if not user.active:
                return jsonify({'message': 'User account is inactive'}), 401
            
            # Generate JWT token
            from config import Config
            payload = {
                'user_id': user.id,
                'email': user.email,
                'roles': [role.name for role in user.roles],
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(days=30)
            }
            
            token = jwt.encode(
                payload,
                Config.JWT_SECRET_KEY,
                algorithm='HS256'
            )
            
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'roles': [role.name for role in user.roles]
                }
            }), 200
        except Exception as e:
            return jsonify({'message': f'Login failed: {str(e)}'}), 500
    
    @bp.route('/profile', methods=['GET'])
    def get_profile():
        """Get current user profile (requires authentication)"""
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Missing or invalid authorization header'}), 401
        
        try:
            from config import Config
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            return jsonify({
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'address': user.address,
                'roles': [role.name for role in user.roles]
            }), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500
    
    @bp.route('/profile', methods=['PUT'])
    def update_profile():
        """Update user profile"""
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Missing or invalid authorization header'}), 401
        
        try:
            from config import Config
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'message': 'User not found'}), 404
            
            data = request.get_json()
            
            # Update allowed fields
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'phone' in data:
                user.phone = data['phone']
            if 'address' in data:
                user.address = data['address']
            
            db.session.commit()
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'address': user.address
                }
            }), 200
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error: {str(e)}'}), 500
