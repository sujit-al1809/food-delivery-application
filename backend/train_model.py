"""
Script to train the ETA prediction ML model

This script creates synthetic training data and trains a Linear Regression model
to predict delivery time based on:
- Distance (km)
- Number of items in order
- Hour of day

The model is saved as eta_model.pkl and loaded on app startup.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pickle
import os

def generate_synthetic_data(n_samples=1000):
    """
    Generate synthetic training data for ETA prediction
    
    Features:
    - distance_km: 1-15 km
    - order_items: 1-10 items
    - hour_of_day: 0-23 hours
    """
    np.random.seed(42)
    
    # Generate random features
    distances = np.random.uniform(1, 15, n_samples)
    order_items = np.random.randint(1, 11, n_samples)
    hours = np.random.randint(0, 24, n_samples)
    
    # Create realistic target (delivery time in minutes)
    # Base time: 10 minutes
    # Distance: 2-2.5 min per km
    # Items: 3 min per item for prep
    # Peak hours (11-2, 6-9pm): +10 minutes
    
    base_time = 10
    distance_time = distances * np.random.uniform(2, 2.5, n_samples)
    prep_time = order_items * 3
    
    # Peak hours surcharge
    peak_surcharge = np.zeros(n_samples)
    peak_hours = [11, 12, 13, 18, 19, 20]
    for i in range(n_samples):
        if hours[i] in peak_hours:
            peak_surcharge[i] = 10
    
    # Add some random noise
    noise = np.random.normal(0, 2, n_samples)
    
    delivery_times = base_time + distance_time + prep_time + peak_surcharge + noise
    delivery_times = np.clip(delivery_times, 15, 120)  # Between 15-120 minutes
    
    X = np.column_stack([distances, order_items, hours])
    y = delivery_times
    
    return X, y

def train_model(output_path='instance/eta_model.pkl'):
    """
    Train the ETA prediction model
    
    Args:
        output_path: Path to save the trained model
    """
    print("Generating synthetic training data...")
    X_train, y_train = generate_synthetic_data(n_samples=1000)
    
    print("Training Linear Regression model...")
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Print model details
    print(f"\nModel trained successfully!")
    print(f"Coefficients: {model.coef_}")
    print(f"Intercept: {model.intercept_}")
    print(f"R² Score: {model.score(X_train, y_train):.3f}")
    
    # Test predictions
    print("\nTest predictions:")
    test_cases = [
        [5, 3, 14],    # 5km, 3 items, 2pm
        [10, 5, 18],   # 10km, 5 items, 6pm
        [2, 1, 8],     # 2km, 1 item, 8am
    ]
    
    for features in test_cases:
        pred = model.predict([features])[0]
        print(f"  Distance: {features[0]}km, Items: {features[1]}, Hour: {features[2]} -> {pred:.0f} minutes")
    
    # Save model
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to {output_path}")

if __name__ == '__main__':
    train_model()
