import os
import json
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

class MarketPredictor:
    def __init__(self):
        self.data_file = 'market_data.json'
        self.model_file = 'market_models.json'
        self.price_model = LinearRegression()
        self.profit_model = LinearRegression()
        self.price_scaler = StandardScaler()
        self.profit_scaler = StandardScaler()
        self.price_model_trained = False
        self.profit_model_trained = False
        
    def load_data(self):
        """Load existing market data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        else:
            return []
    
    def save_data(self, data):
        """Save market data to JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_user_data(self, user_id, market_price, harvest_amount, total_cost, total_revenue, net_profit):
        """Add new user data to the dataset."""
        data = self.load_data()
        
        new_row = {
            'user_id': user_id,
            'market_price': market_price,
            'harvest_amount': harvest_amount,
            'total_cost': total_cost,
            'total_revenue': total_revenue,
            'net_profit': net_profit,
            'timestamp': datetime.now().isoformat()
        }
        
        data.append(new_row)
        self.save_data(data)
        
        # Retrain models with new data
        self._train_models()
        
        return data
    
    def clear_user_data(self, user_id):
        """Clear all data for a specific user from the ML model."""
        data = self.load_data()
        # Remove all entries for the specified user
        data = [item for item in data if item['user_id'] != user_id]
        self.save_data(data)
        
        # Retrain models after clearing data
        self._train_models()
    
    def _train_models(self):
        """Train the LinearRegression models with available data."""
        data = self.load_data()
        
        if len(data) < 3:  # Need at least 3 data points for meaningful training
            self.price_model_trained = False
            self.profit_model_trained = False
            return
        
        try:
            # Prepare features for price prediction
            price_features = []
            price_targets = []
            
            # Prepare features for profit prediction
            profit_features = []
            profit_targets = []
            
            for item in data:
                # Features for price prediction: harvest_amount, total_cost
                price_features.append([item['harvest_amount'], item['total_cost']])
                price_targets.append(item['market_price'])
                
                # Features for profit prediction: market_price, harvest_amount, total_cost
                profit_features.append([item['market_price'], item['harvest_amount'], item['total_cost']])
                profit_targets.append(item['net_profit'])
            
            # Convert to numpy arrays
            price_features = np.array(price_features)
            price_targets = np.array(price_targets)
            profit_features = np.array(profit_features)
            profit_targets = np.array(profit_targets)
            
            # Train price prediction model
            if len(price_features) >= 3:
                # Scale features
                price_features_scaled = self.price_scaler.fit_transform(price_features)
                
                # Split data for training
                X_train, X_test, y_train, y_test = train_test_split(
                    price_features_scaled, price_targets, test_size=0.2, random_state=42
                )
                
                # Train model
                self.price_model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = self.price_model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                self.price_model_trained = True
                print(f"Price model trained - MSE: {mse:.2f}, R²: {r2:.2f}")
            
            # Train profit prediction model
            if len(profit_features) >= 3:
                # Scale features
                profit_features_scaled = self.profit_scaler.fit_transform(profit_features)
                
                # Split data for training
                X_train, X_test, y_train, y_test = train_test_split(
                    profit_features_scaled, profit_targets, test_size=0.2, random_state=42
                )
                
                # Train model
                self.profit_model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = self.profit_model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                self.profit_model_trained = True
                print(f"Profit model trained - MSE: {mse:.2f}, R²: {r2:.2f}")
                
        except Exception as e:
            print(f"Error training models: {str(e)}")
            self.price_model_trained = False
            self.profit_model_trained = False
    
    def predict_future_prices(self, periods=12):
        """Predict future market prices using LinearRegression model."""
        if not self.price_model_trained:
            return None, "Model not trained. Need at least 3 data points."
        
        try:
            data = self.load_data()
            if len(data) == 0:
                return None, "No data available for prediction."
            
            # Get recent data for prediction
            recent_data = data[-min(5, len(data)):]  # Use last 5 data points or all if less
            
            future_predictions = []
            current_date = datetime.now()
            
            for i in range(1, periods + 1):
                future_date = current_date + timedelta(days=i*30)  # Monthly predictions
                
                # Use average values from recent data for prediction
                avg_harvest = np.mean([item['harvest_amount'] for item in recent_data])
                avg_cost = np.mean([item['total_cost'] for item in recent_data])
                
                # Prepare features
                features = np.array([[avg_harvest, avg_cost]])
                features_scaled = self.price_scaler.transform(features)
                
                # Make prediction
                predicted_price = self.price_model.predict(features_scaled)[0]
                
                # Ensure non-negative price
                predicted_price = max(0, predicted_price)
                
                future_predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_price': round(predicted_price, 2)
                })
            
            return future_predictions, None
            
        except Exception as e:
            return None, f"Error generating price predictions: {str(e)}"
    
    def predict_future_profits(self, periods=12):
        """Predict future profits using LinearRegression model."""
        if not self.profit_model_trained:
            return None, "Model not trained. Need at least 3 data points."
        
        try:
            data = self.load_data()
            if len(data) == 0:
                return None, "No data available for prediction."
            
            # Get recent data for prediction
            recent_data = data[-min(5, len(data)):]  # Use last 5 data points or all if less
            
            future_predictions = []
            current_date = datetime.now()
            
            for i in range(1, periods + 1):
                future_date = current_date + timedelta(days=i*30)  # Monthly predictions
                
                # Use average values from recent data for prediction
                avg_price = np.mean([item['market_price'] for item in recent_data])
                avg_harvest = np.mean([item['harvest_amount'] for item in recent_data])
                avg_cost = np.mean([item['total_cost'] for item in recent_data])
                
                # Prepare features
                features = np.array([[avg_price, avg_harvest, avg_cost]])
                features_scaled = self.profit_scaler.transform(features)
                
                # Make prediction
                predicted_profit = self.profit_model.predict(features_scaled)[0]
                
                future_predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_profit': round(predicted_profit, 2)
                })
            
            return future_predictions, None
            
        except Exception as e:
            return None, f"Error generating profit predictions: {str(e)}"
    
    def get_historical_data(self, user_id=None, limit=3):
        """Get historical data for visualization."""
        data = self.load_data()
        
        # If user_id is provided, filter data for that user only
        if user_id is not None:
            data = [item for item in data if item['user_id'] == user_id]
        
        if len(data) == 0:
            return []
        
        # Sort by timestamp and get the most recent data
        sorted_data = sorted(data, key=lambda x: x['timestamp'], reverse=True)
        recent_data = sorted_data[:limit]
        
        # Format for chart display
        historical_data = []
        for i, item in enumerate(recent_data):
            historical_data.append({
                'month': f"Month {i+1}",
                'market_price': item['market_price'],
                'net_profit': item['net_profit']
            })
        
        return historical_data

    def get_model_stats(self, user_id=None):
        """Get statistics about the data and model performance."""
        data = self.load_data()
        
        # If user_id is provided, filter data for that user only
        if user_id is not None:
            data = [item for item in data if item['user_id'] == user_id]
        
        if len(data) == 0:
            return {
                'total_data_points': 0,
                'model_trained': False,
                'message': 'No data available',
                'avg_market_price': 0,
                'avg_profit': 0,
                'total_users': 1 if user_id is not None else 0,
                'model_type': 'LinearRegression',
                'training_status': 'Not trained'
            }
        
        try:
            prices = [item['market_price'] for item in data]
            profits = [item['net_profit'] for item in data]
            user_ids = list(set([item['user_id'] for item in data]))
            
            # Calculate model performance metrics if models are trained
            model_performance = {}
            if self.price_model_trained and len(data) >= 3:
                try:
                    # Prepare test data for evaluation
                    price_features = np.array([[item['harvest_amount'], item['total_cost']] for item in data])
                    price_targets = np.array(prices)
                    
                    # Scale features
                    price_features_scaled = self.price_scaler.transform(price_features)
                    
                    # Make predictions
                    price_predictions = self.price_model.predict(price_features_scaled)
                    
                    # Calculate metrics
                    price_mse = mean_squared_error(price_targets, price_predictions)
                    price_r2 = r2_score(price_targets, price_predictions)
                    
                    model_performance['price_model'] = {
                        'mse': round(price_mse, 2),
                        'r2_score': round(price_r2, 3)
                    }
                except Exception as e:
                    model_performance['price_model'] = {'error': str(e)}
            
            if self.profit_model_trained and len(data) >= 3:
                try:
                    # Prepare test data for evaluation
                    profit_features = np.array([[item['market_price'], item['harvest_amount'], item['total_cost']] for item in data])
                    profit_targets = np.array(profits)
                    
                    # Scale features
                    profit_features_scaled = self.profit_scaler.transform(profit_features)
                    
                    # Make predictions
                    profit_predictions = self.profit_model.predict(profit_features_scaled)
                    
                    # Calculate metrics
                    profit_mse = mean_squared_error(profit_targets, profit_predictions)
                    profit_r2 = r2_score(profit_targets, profit_predictions)
                    
                    model_performance['profit_model'] = {
                        'mse': round(profit_mse, 2),
                        'r2_score': round(profit_r2, 3)
                    }
                except Exception as e:
                    model_performance['profit_model'] = {'error': str(e)}
            
            stats = {
                'total_data_points': len(data),
                'model_trained': self.price_model_trained and self.profit_model_trained,
                'avg_market_price': round(sum(prices) / len(prices), 2) if prices else 0,
                'avg_profit': round(sum(profits) / len(profits), 2) if profits else 0,
                'total_users': len(user_ids),
                'model_type': 'LinearRegression',
                'training_status': 'Trained' if (self.price_model_trained and self.profit_model_trained) else 'Partially trained',
                'model_performance': model_performance,
                'date_range': {
                    'start': min([item['timestamp'] for item in data]),
                    'end': max([item['timestamp'] for item in data])
                }
            }
            
            return stats
            
        except Exception as e:
            return {
                'total_data_points': len(data),
                'model_trained': False,
                'message': f'Error calculating stats: {str(e)}',
                'avg_market_price': 0,
                'avg_profit': 0,
                'total_users': 1 if user_id is not None else 0,
                'model_type': 'LinearRegression',
                'training_status': 'Error'
            }

# Global instance
market_predictor = MarketPredictor()
