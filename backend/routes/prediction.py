from flask import request, jsonify
import pickle
import os
import numpy as np
from config import Config

def register_routes(bp):
    """Register prediction routes"""
    
    # Load ML model on startup
    model = None
    model_loaded = False
    
    def load_model():
        global model, model_loaded
        try:
            if os.path.exists(Config.MODEL_PATH):
                with open(Config.MODEL_PATH, 'rb') as f:
                    model = pickle.load(f)
                model_loaded = True
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
        return False
    
    @bp.route('/predict-eta', methods=['POST'])
    def predict_eta():
        """Predict delivery time using ML model"""
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['distance_km', 'order_items', 'hour_of_day']
        if not all(field in data for field in required_fields):
            return jsonify({
                'message': f'Missing required fields: {", ".join(required_fields)}'
            }), 400
        
        try:
            # Load model if not already loaded
            if not model_loaded:
                load_model()
            
            if model is None:
                # Return default estimate if model not available
                # Formula: base time + distance time + prep time
                distance_km = float(data['distance_km'])
                order_items = int(data['order_items'])
                hour_of_day = int(data['hour_of_day'])
                
                # Simple heuristic when model not available
                base_time = 10
                distance_time = distance_km * 2  # 2 min per km
                prep_time = order_items * 3  # 3 min per item
                
                # Peak hours (11-2pm, 6-9pm) add 10 minutes
                peak_hours = [11, 12, 13, 18, 19, 20]
                peak_surcharge = 10 if hour_of_day in peak_hours else 0
                
                estimated_minutes = int(base_time + distance_time + prep_time + peak_surcharge)
                
                return jsonify({
                    'estimated_minutes': max(15, estimated_minutes),  # Minimum 15 minutes
                    'note': 'Model not available, using heuristic estimation'
                }), 200
            
            # Prepare features for prediction
            distance_km = float(data['distance_km'])
            order_items = int(data['order_items'])
            hour_of_day = int(data['hour_of_day'])
            
            # Features: [distance_km, order_items, hour_of_day]
            features = np.array([[distance_km, order_items, hour_of_day]])
            
            # Make prediction
            prediction = model.predict(features)[0]
            estimated_minutes = max(15, int(prediction))  # Minimum 15 minutes
            
            return jsonify({
                'estimated_minutes': estimated_minutes,
                'distance_km': distance_km,
                'order_items': order_items,
                'hour_of_day': hour_of_day
            }), 200
        except (ValueError, TypeError) as e:
            return jsonify({'message': f'Invalid input format: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'message': f'Error predicting ETA: {str(e)}'}), 500
    
    @bp.route('/predict-eta/batch', methods=['POST'])
    def predict_eta_batch():
        """Batch predict delivery times"""
        data = request.get_json()
        
        if not data or 'orders' not in data:
            return jsonify({'message': 'orders array is required'}), 400
        
        try:
            # Load model if not already loaded
            if not model_loaded:
                load_model()
            
            predictions = []
            
            for order in data['orders']:
                required_fields = ['distance_km', 'order_items', 'hour_of_day']
                if not all(field in order for field in required_fields):
                    predictions.append({'error': 'Missing required fields'})
                    continue
                
                distance_km = float(order['distance_km'])
                order_items = int(order['order_items'])
                hour_of_day = int(order['hour_of_day'])
                
                if model is None:
                    # Heuristic
                    base_time = 10
                    distance_time = distance_km * 2
                    prep_time = order_items * 3
                    peak_hours = [11, 12, 13, 18, 19, 20]
                    peak_surcharge = 10 if hour_of_day in peak_hours else 0
                    estimated_minutes = int(base_time + distance_time + prep_time + peak_surcharge)
                else:
                    # ML prediction
                    features = np.array([[distance_km, order_items, hour_of_day]])
                    estimated_minutes = int(model.predict(features)[0])
                
                predictions.append({
                    'estimated_minutes': max(15, estimated_minutes),
                    'distance_km': distance_km,
                    'order_items': order_items,
                    'hour_of_day': hour_of_day
                })
            
            return jsonify({'predictions': predictions}), 200
        except Exception as e:
            return jsonify({'message': f'Error in batch prediction: {str(e)}'}), 500
    
    # Load model on route initialization
    load_model()
