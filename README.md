# WeatherGuard Harvest

A Flask-based weather forecasting application designed for farmers in Sri Lanka, specifically focused on the Anuradhapura region. The application includes advanced machine learning capabilities for market predictions and analytics.

## Features

- **Real-time Weather Data**: Get current weather conditions and 7-day forecasts for 12 Sri Lankan cities
- **User Authentication**: Secure user registration, login, and profile management
- **Agricultural Focus**: Tailored for farming communities with location-specific weather data
- **Responsive Design**: Mobile-friendly interface with modern UI/UX
- **Weather API Integration**: Uses Open-Meteo API for accurate weather data
- **Smart Analytics**: Machine learning-powered market predictions for farmers
- **Cost-Profit Analysis**: Tools for calculating and analyzing farming profitability
- **Linear Regression Models**: Advanced ML models for price and profit predictions

## Supported Cities

- Anuradhapura, Mihintale, Kekirawa, Medawachchiya
- Habarana, Eppawala, Galenbindunuwewa, Galnewa
- Horowupotana, Kahatagasdigiliya, Bulnewa, Ganewalpola

## Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to `http://localhost:5000`

## Smart Analytics Features

### Future Analyse Button
- **Location**: Home page (index.html) in the Smart Analytics section
- **Functionality**: Navigates to the analytics.html page
- **Access**: Available to logged-in users only

### Add My Details Button (Cost-Profit Analysis Tool)
- **Location**: Cost-Profit Analysis Tool page (cost_profit_analysis.html)
- **Functionality**: Allows users to submit their market data for ML analysis
- **Features**:
  - Larger button size for emphasis
  - Displays explanatory note: "Adding your data for analysing future market behaviors"
  - Only appears after profit calculation is completed
  - Stores user data for machine learning analysis

### Machine Learning Component (ml_model.py)
- **File**: `ml_model.py`
- **Algorithm**: Linear Regression with scikit-learn
- **Features**:
  - Takes prices and profits as input
  - Predicts future prices and profits using LinearRegression
  - Uses feature scaling and train-test split for validation
  - Stores data in JSON format for persistence
  - Provides model statistics and performance metrics

### Analytics Page (analytics.html)
- **URL**: `/analytics`
- **Features**:
  - Trading-style charts using Chart.js
  - Future price predictions graph
  - Future profit predictions graph
  - Model statistics dashboard with performance metrics
  - Responsive design for mobile devices

## Machine Learning Implementation

### Model Architecture
```
Price Prediction Model:
- Features: [harvest_amount, total_cost]
- Target: market_price
- Algorithm: LinearRegression

Profit Prediction Model:
- Features: [market_price, harvest_amount, total_cost]
- Target: net_profit
- Algorithm: LinearRegression
```

### Training Process
1. **Data Preparation**: Extract features and targets from user data
2. **Feature Scaling**: Normalize features using StandardScaler
3. **Train-Test Split**: 80% for training, 20% for validation
4. **Model Training**: Fit LinearRegression on training data
5. **Performance Evaluation**: Calculate MSE and R² on test data
6. **Model Storage**: Keep trained models in memory for predictions

### Benefits of LinearRegression
- **Mathematically sound**: Based on linear relationships between variables
- **Statistically validated**: Performance metrics (MSE, R²) provide confidence
- **Feature-aware**: Considers relationships between harvest amounts, costs, and outcomes
- **Automatically adaptive**: Improves predictions as more data becomes available
- **Professional-grade**: Uses industry-standard scikit-learn implementation

## User Data Flow

1. **Data Collection**: Users submit their information through the Cost-Profit Analysis Tool
2. **Data Storage**: Information is stored in `market_data.json`
3. **Analysis**: ML model analyzes patterns in the collected data
4. **Prediction**: System generates future market predictions
5. **Visualization**: Results are displayed in trading-style charts

## Technical Implementation

### Data Structure
```json
{
  "user_id": 1,
  "market_price": 150.0,
  "harvest_amount": 100.0,
  "total_cost": 8000.0,
  "total_revenue": 15000.0,
  "net_profit": 7000.0,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Chart Features
- **Interactive**: Hover effects and tooltips
- **Responsive**: Adapts to different screen sizes
- **Professional**: Trading-style appearance similar to ExpertOption/TradingView
- **Color-coded**: Green for profits, blue for prices

## Usage Instructions

### For Users
1. **Calculate Profit**: Go to Cost-Profit Analysis Tool and complete your calculations
2. **Add Data**: Click "Add My Details" to contribute to the ML model
3. **View Analytics**: Click "Future Analyse" to see predictions
4. **Monitor Trends**: Check the charts for future market insights

### For Developers
1. **Start Application**: Run `python app.py` to start the Flask server
2. **Access Analytics**: Navigate to `/analytics` to view the predictions

## Troubleshooting

### Database Schema Issues

If you encounter errors like `no such column: user.profile_picture`, the database schema is out of sync with the current models.

**Quick Fix:**
```bash
python fix_database.py
```

**Manual Fix:**
1. Delete the database file: `instance/users.db`
2. Restart the application: `python app.py`

**Advanced Migration:**
```bash
python migrate_db.py
```

## Recent Fixes Applied

### 1. **Missing Template Filters**
- Added `weather_code_to_text` filter to convert weather codes to human-readable text
- Added `datetime_format` filter to format dates properly

### 2. **Missing Template Functions**
- Made `weather_code_to_icon` function available in templates
- Fixed template syntax errors

### 3. **File Organization**
- Moved `requirements.txt` from `templates/` to root directory
- Added missing `pytz` dependency

### 4. **Error Handling**
- Added try-catch blocks for database operations
- Improved error handling for weather API calls
- Added 500 error handler

### 5. **CSS Styling**
- Added missing user menu styling
- Added search section styling
- Replaced missing weather icon images with emoji-based icons
- Fixed footer formatting across all templates

### 6. **Template Improvements**
- Added flash message display to index page
- Fixed weather search functionality
- Updated all footers to use consistent branding
- Removed duplicate macro definitions

### 7. **Database Safety**
- Added database rollback on errors
- Improved user loader error handling

### 8. **Machine Learning Enhancements**
- Replaced heuristic model with LinearRegression
- Added proper ML dependencies (scikit-learn, numpy)
- Implemented feature scaling and model validation
- Added performance metrics and statistics

## Project Structure

```
WeatherGuard Harvest/
├── app.py                 # Main Flask application
├── ml_model.py           # Machine learning prediction engine
├── requirements.txt       # Python dependencies
├── fix_database.py       # Database fix utility
├── migrate_db.py         # Database migration utility
├── market_data.json      # ML data storage
├── README.md             # This file
├── instance/
│   └── users.db         # SQLite database
├── static/
│   ├── style.css        # Main stylesheet
│   └── images/
│       └── background.jpg
└── templates/
    ├── index.html        # Home page
    ├── weather.html      # Weather forecast page
    ├── analytics.html    # Analytics page with charts
    ├── cost_profit_analysis.html # Cost-profit analysis tool
    ├── login.html        # Login page
    ├── signup.html       # Registration page
    ├── profile.html      # User profile
    ├── settings.html     # User settings
    ├── support.html      # Support page
    └── 404.html         # Error page
```

## API Integration

The application integrates with the Open-Meteo API to provide:
- Current weather conditions (temperature, humidity, wind, precipitation)
- 7-day weather forecasts
- Weather code mapping to user-friendly descriptions

## Security Features

- Password hashing using PBKDF2 with SHA256
- CSRF protection with Flask-WTF
- User session management with Flask-Login
- Input validation and sanitization
- User data anonymization in analytics

## Dependencies

- Flask and Flask extensions
- scikit-learn 1.3.0 (for ML models)
- numpy 1.24.3 (for numerical operations)
- Chart.js (CDN - no installation required)
- Standard Python libraries (json, datetime, random)

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile-responsive design
- Progressive enhancement approach

## Development

The application runs in debug mode by default. For production:
1. Set `SECRET_KEY` environment variable
2. Disable debug mode
3. Use a production WSGI server
4. Configure proper logging

## Future Enhancements

- **Cross-validation** for more robust model evaluation
- **Hyperparameter tuning** for optimal model performance
- **Feature selection** to identify most important variables
- **Model persistence** to save trained models between sessions
- **Ensemble methods** combining multiple algorithms for better predictions
- **Real-time data updates**
- **Seasonal trend analysis**
- **Weather correlation modeling**
- **Export functionality for predictions**

## License

© 2024 WeatherGuard Harvest. All rights reserved.
