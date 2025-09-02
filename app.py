import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
import requests
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from ml_model import market_predictor

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secure_random_key')  # Use env var
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Template Filters ---
@app.template_filter('weather_code_to_text')
def weather_code_to_text(code):
    """Convert weather code to human-readable text."""
    mapping = {
        0: 'Clear sky',
        1: 'Mainly clear',
        2: 'Partly cloudy',
        3: 'Overcast',
        45: 'Foggy',
        48: 'Depositing rime fog',
        51: 'Light drizzle',
        53: 'Moderate drizzle',
        55: 'Dense drizzle',
        56: 'Light freezing drizzle',
        57: 'Dense freezing drizzle',
        61: 'Slight rain',
        63: 'Moderate rain',
        65: 'Heavy rain',
        66: 'Light freezing rain',
        67: 'Heavy freezing rain',
        71: 'Slight snow fall',
        73: 'Moderate snow fall',
        75: 'Heavy snow fall',
        77: 'Snow grains',
        80: 'Slight rain showers',
        81: 'Moderate rain showers',
        82: 'Violent rain showers',
        85: 'Slight snow showers',
        86: 'Heavy snow showers',
        95: 'Thunderstorm',
        96: 'Thunderstorm with slight hail',
        99: 'Thunderstorm with heavy hail'
    }
    return mapping.get(code, 'Unknown')

@app.template_filter('datetime_format')
def datetime_format(date_str):
    """Format date string to readable format."""
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime('%B %d, %Y')
        return str(date_str)
    except:
        return str(date_str)

# --- Models ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)



# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class SettingsForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

# --- Helpers ---
def get_greeting():
    try:
        tz = pytz.timezone('Asia/Colombo')
        hour = datetime.now(tz).hour
        if hour < 12:
            return "Good Morning"
        elif hour < 17:
            return "Good Afternoon"
        else:
            return "Good Evening"
    except:
        return "Hello"

def get_weather_data(city):
    """Fetch weather data from Open-Meteo API."""
    # Coordinates for predefined cities (latitude, longitude)
    cities = {
        'Anuradhapura': (8.3114, 80.4037),
        'Mihintale': (8.3594, 80.5006),
        'Kekirawa': (8.0333, 80.5833),
        'Medawachchiya': (8.5333, 80.4667),
        'Habarana': (8.0333, 80.75),
        'Eppawala': (8.1333, 80.5167),
        'Galenbindunuwewa': (8.3167, 80.6333),
        'Galnewa': (8.2, 80.5667),
        'Horowupotana': (8.9667, 80.8167),
        'Kahatagasdigiliya': (8.9667, 80.6667),
        'Bulnewa': (8.3167, 80.3167),
        'Ganewalpola': (8.3167, 80.3167)
    }
    
    if city not in cities:
        return None
    
    lat, lon = cities[city]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia/Colombo"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Weather API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def weather_code_to_icon(code):
    """Map Open-Meteo weather code to icon class."""
    mapping = {
        0: 'clear-sky',
        1: 'mainly-clear',
        2: 'partly-cloudy',
        3: 'overcast',
        45: 'fog',
        48: 'fog',
        51: 'light-rain',
        53: 'moderate-rain',
        55: 'heavy-rain',
        56: 'light-rain',
        57: 'heavy-rain',
        61: 'light-rain',
        63: 'moderate-rain',
        65: 'heavy-rain',
        66: 'light-rain',
        67: 'heavy-rain',
        71: 'snow',
        73: 'snow',
        75: 'snow',
        77: 'snow',
        80: 'light-rain',
        81: 'moderate-rain',
        82: 'heavy-rain',
        85: 'snow',
        86: 'snow',
        95: 'thunderstorm',
        96: 'thunderstorm',
        99: 'thunderstorm'
    }
    return mapping.get(code, 'clear-sky')

# --- Routes ---
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def home():
    greeting = get_greeting() if current_user.is_authenticated else None
    search_result = None
    if request.method == 'POST' and current_user.is_authenticated:
        city = request.form.get('city')
        if city:
            search_result = get_weather_data(city)
            if not search_result:
                flash('Unable to fetch weather data. Please try again.', 'error')
        else:
            flash('Please select a city.', 'error')
    return render_template('index.html', greeting=greeting, user=current_user, search_result=search_result, weather_code_to_icon=weather_code_to_icon)

@app.route('/weather', methods=['GET', 'POST'])
@login_required
def weather():
    greeting = get_greeting()
    weather_data = None
    selected_city = None
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            selected_city = city
            weather_data = get_weather_data(city)
            if not weather_data:
                flash('Unable to fetch weather data. Please try again.', 'error')
        else:
            flash('Please select a city.', 'error')
    return render_template('weather.html', greeting=greeting, user=current_user, weather_data=weather_data, selected_city=selected_city, weather_code_to_icon=weather_code_to_icon)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
        elif User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
        else:
            try:
                hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
                new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                flash('Account created! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('Error creating account. Please try again.', 'error')
                print(f"User creation error: {e}")
    return render_template('signup.html', form=form)

@app.route('/support', methods=['GET', 'POST'])
@login_required
def support():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if name and email and message and len(message) <= 500:  # Basic validation
            flash('Your message has been sent!', 'success')
        else:
            flash('Please fill out all fields correctly (message max 500 characters).', 'error')
        return redirect(url_for('support'))
    greeting = get_greeting()
    return render_template('support.html', greeting=greeting, user=current_user)

@app.route('/profile')
@login_required
def profile():
    greeting = get_greeting()
    return render_template('profile.html', greeting=greeting, user=current_user)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            if form.new_password.data == form.current_password.data:
                flash('New password cannot be the same as the current password.', 'error')
            else:
                try:
                    current_user.password = generate_password_hash(form.new_password.data, method='pbkdf2:sha256')
                    db.session.commit()
                    flash('Password updated successfully!', 'success')
                    return redirect(url_for('profile'))
                except Exception as e:
                    db.session.rollback()
                    flash('Error updating password. Please try again.', 'error')
                    print(f"Password update error: {e}")
        else:
            flash('Current password is incorrect.', 'error')
    greeting = get_greeting()
    return render_template('settings.html', greeting=greeting, user=current_user, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))





@app.route('/cost-profit-analysis', methods=['GET', 'POST'])
@login_required
def cost_profit_analysis():
    """Cost-Profit Analysis Tool with 3-block layout."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'generate_pdf':
            return generate_cost_profit_pdf()
        elif action == 'add_to_ml':
            return handle_add_to_ml()
    
    return render_template('cost_profit_analysis.html', user=current_user)

@app.route('/analytics', methods=['GET', 'POST'])
@login_required
def analytics():
    """Analytics page with ML predictions."""
    
    # Handle clear data request
    if request.method == 'POST' and request.form.get('clear_data'):
        try:
            # Clear ML model data for the current user
            market_predictor.clear_user_data(current_user.id)
            
            flash('All your data has been cleared successfully!', 'success')
        except Exception as e:
            flash('Error clearing data. Please try again.', 'error')
            print(f"Error clearing data: {e}")
    
    # Get model statistics for the current user
    stats = market_predictor.get_model_stats(current_user.id)
    
    # Get historical data
    historical_data = market_predictor.get_historical_data(current_user.id, limit=3)
    
    # Get predictions
    price_predictions, price_error = market_predictor.predict_future_prices(periods=3)
    profit_predictions, profit_error = market_predictor.predict_future_profits(periods=3)
    
    return render_template('analytics.html', 
                         user=current_user,
                         stats=stats,
                         historical_data=historical_data,
                         price_predictions=price_predictions,
                         profit_predictions=profit_predictions,
                         price_error=price_error,
                         profit_error=profit_error)

def generate_cost_profit_pdf():
    """Generate PDF report for cost-profit analysis tool."""
    try:
        # Get data from form
        total_cost = float(request.form.get('total_cost', 0))
        total_revenue = float(request.form.get('total_revenue', 0))
        net_profit = float(request.form.get('net_profit', 0))
        market_price = float(request.form.get('market_price', 0))
        harvest_amount = float(request.form.get('harvest_amount', 0))
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#388659')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#388659')
        )
        
        normal_style = styles['Normal']
        
        # Add title
        story.append(Paragraph("Cost-Profit Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Add date and user info
        current_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Generated on: {current_date}", normal_style))
        story.append(Paragraph(f"User: {current_user.username}", normal_style))
        story.append(Spacer(1, 20))
        
        # Create detailed data table
        data = [
            ['Parameter', 'Value', 'Details'],
            ['Market Price (per kg)', f"Rs. {market_price:,.2f}", 'Current market rate'],
            ['Harvest Amount', f"{harvest_amount:,.2f} kg", 'Total harvest quantity'],
            ['Total Revenue', f"Rs. {total_revenue:,.2f}", f'{market_price:,.2f} × {harvest_amount:,.2f}'],
            ['Total Cost', f"Rs. {total_cost:,.2f}", 'Initial + Subsequent costs'],
            ['Net Profit/Loss', f"Rs. {net_profit:,.2f}", f'{total_revenue:,.2f} - {total_cost:,.2f}']
        ]
        
        # Create table with enhanced styling
        table = Table(data, colWidths=[2.5*inch, 2*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#388659')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Add comprehensive analysis
        story.append(Paragraph("Detailed Analysis:", heading_style))
        
        if net_profit >= 0:
            profit_status = "✅ Profitable Business"
            profit_margin = (net_profit / total_revenue) * 100 if total_revenue > 0 else 0
            story.append(Paragraph(f"Status: {profit_status}", normal_style))
            story.append(Paragraph(f"Profit Margin: {profit_margin:.2f}%", normal_style))
            story.append(Paragraph(f"Return on Investment: {(net_profit / total_cost) * 100:.2f}%" if total_cost > 0 else "N/A", normal_style))
        else:
            profit_status = "⚠️ Loss Incurred"
            loss_percentage = (abs(net_profit) / total_revenue) * 100 if total_revenue > 0 else 0
            story.append(Paragraph(f"Status: {profit_status}", normal_style))
            story.append(Paragraph(f"Loss Percentage: {loss_percentage:.2f}%", normal_style))
        
        # Add recommendations
        story.append(Spacer(1, 15))
        story.append(Paragraph("Recommendations:", heading_style))
        
        if net_profit >= 0:
            story.append(Paragraph("• Continue with current farming practices", normal_style))
            story.append(Paragraph("• Consider scaling up production if market conditions remain favorable", normal_style))
            story.append(Paragraph("• Monitor market prices for optimal selling timing", normal_style))
        else:
            story.append(Paragraph("• Review and optimize cost structure", normal_style))
            story.append(Paragraph("• Consider alternative crops or markets", normal_style))
            story.append(Paragraph("• Analyze cost reduction opportunities", normal_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Return PDF as download
        from flask import send_file
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'cost_profit_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('cost_profit_analysis'))

def handle_add_to_ml():
    """Handle adding data to ML model for analysis."""
    try:
        # Get data from form
        total_cost = float(request.form.get('total_cost', 0))
        total_revenue = float(request.form.get('total_revenue', 0))
        net_profit = float(request.form.get('net_profit', 0))
        market_price = float(request.form.get('market_price', 0))
        harvest_amount = float(request.form.get('harvest_amount', 0))
        
        # Validate data
        if not all([total_cost > 0, total_revenue > 0, market_price > 0, harvest_amount > 0]):
            return {'success': False, 'message': 'Invalid data provided'}
        
        # Add data to ML model
        market_predictor.add_user_data(
            user_id=current_user.id,
            market_price=market_price,
            harvest_amount=harvest_amount,
            total_cost=total_cost,
            total_revenue=total_revenue,
            net_profit=net_profit
        )
        
        return jsonify({'success': True, 'message': 'Data successfully added to analysis'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('404.html'), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            # Try to create tables
            db.create_all()
            print("[OK] Database initialized successfully")
        except Exception as e:
            if "no such column" in str(e):
                print("[WARNING] Database schema mismatch detected!")
                print("   Resetting database to match current models...")
                try:
                    # Drop and recreate all tables
                    db.drop_all()
                    db.create_all()
                    print("[OK] Database reset and initialized successfully")
                except Exception as reset_error:
                    print(f"[ERROR] Database reset failed: {reset_error}")
                    print("   Please manually delete 'instance/users.db' and restart")
                    sys.exit(1)
            else:
                print(f"[ERROR] Database initialization failed: {e}")
                sys.exit(1)

    app.run(debug=True)
