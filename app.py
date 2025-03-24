from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from deep_translator import GoogleTranslator
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import time
from functools import wraps
import math
import requests
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    handlers=[RotatingFileHandler('app.log', maxBytes=100000, backupCount=3, delay=True)],
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Example emergency services data
EMERGENCY_SERVICES = {
    'police': [
        {'name': 'Central Police Station', 'coordinates': (28.6139, 77.2090), 'phone': '911'},
        {'name': 'North Police Station', 'coordinates': (28.6239, 77.2190), 'phone': '911'},
        {'name': 'South Police Station', 'coordinates': (28.6039, 77.1990), 'phone': '911'}
    ],
    'hospital': [
        {'name': 'City General Hospital', 'coordinates': (28.6139, 77.2090), 'phone': '911'},
        {'name': 'Medical Center', 'coordinates': (28.6239, 77.2190), 'phone': '911'},
        {'name': 'Community Hospital', 'coordinates': (28.6039, 77.1990), 'phone': '911'}
    ],
    'fire': [
        {'name': 'Main Fire Station', 'coordinates': (28.6139, 77.2090), 'phone': '911'},
        {'name': 'East Fire Station', 'coordinates': (28.6239, 77.2190), 'phone': '911'},
        {'name': 'West Fire Station', 'coordinates': (28.6039, 77.1990), 'phone': '911'}
    ]
}

def retry_on_failure(max_retries=3, delay=1):
    """Retry a function multiple times if it fails"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logging.error(f"Error in {func.__name__}: {e}")
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@app.route('/')
def home():
    """Render the home page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error rendering home page: {str(e)}")
        logging.error(f"Template path: {os.path.join(os.getcwd(), 'templates', 'index.html')}")
        return f"Error loading page: {str(e)}", 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/translate', methods=['POST'])
@retry_on_failure(max_retries=3)
def translate_text():
    """Translate text to another language"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        target_lang = data.get('target_lang', 'en')

        if not text:
            return jsonify({'error': 'Empty text provided'}), 400
        
        # Create a new translator instance for each request
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated_text = translator.translate(text)
        
        return jsonify({
            'original_text': text,
            'translated_text': translated_text,
            'target_language': target_lang
        })
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        return jsonify({'error': 'Translation service error'}), 500

@app.route('/detect-language', methods=['POST'])
@retry_on_failure(max_retries=3)
def detect_language():
    """Detect the language of input text"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Empty text provided'}), 400

        # Create a new translator instance for detection
        translator = GoogleTranslator(source='auto', target='en')
        detected_lang = translator.detect(text)

        return jsonify({
            'text': text,
            'detected_language': detected_lang
        })
    except Exception as e:
        logging.error(f"Language detection error: {str(e)}")
        return jsonify({'error': 'Language detection service error'}), 500

def search_osm_services(lat, lon, service_type, radius=5000):
    """Search for emergency services using OpenStreetMap's Nominatim API"""
    try:
        # Define search terms for different service types
        search_terms = {
            'police': 'police station',
            'hospital': 'hospital',
            'fire': 'fire station'
        }
        
        if service_type not in search_terms:
            return None
            
        # Construct the search query
        query = f"{search_terms[service_type]} near {lat},{lon}"
        encoded_query = quote(query)
        
        # Make request to Nominatim API
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_query}&format=json&limit=5&addressdetails=1"
        headers = {
            'User-Agent': 'EmergencyServicesApp/1.0'  # Required by Nominatim's terms of service
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        results = response.json()
        
        if not results:
            return None
            
        # Find the nearest service within radius
        nearest = None
        min_distance = float('inf')
        
        for result in results:
            service_lat = float(result['lat'])
            service_lon = float(result['lon'])
            
            distance = calculate_distance(lat, lon, service_lat, service_lon)
            
            if distance < min_distance and distance <= radius/1000:  # Convert radius to km
                min_distance = distance
                nearest = {
                    'name': result.get('display_name', 'Unknown'),
                    'distance': min_distance,
                    'coordinates': (service_lat, service_lon),
                    'address': result.get('address', {}),
                    'phone': result.get('address', {}).get('phone', 'N/A')
                }
        
        return nearest
        
    except Exception as e:
        logging.error(f"Error searching OSM services: {str(e)}")
        return None

@app.route('/api/emergency/nearest', methods=['POST'])
@retry_on_failure(max_retries=3)
def get_nearest_services():
    """Get the nearest emergency services based on user location"""
    try:
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'error': 'Location coordinates required'}), 400
        
        user_lat = float(data['latitude'])
        user_lon = float(data['longitude'])
        
        # Search for each type of service
        result = {
            'police': search_osm_services(user_lat, user_lon, 'police'),
            'hospital': search_osm_services(user_lat, user_lon, 'hospital'),
            'fire': search_osm_services(user_lat, user_lon, 'fire')
        }
        
        # Format the response
        formatted_result = {}
        for service_type, service_data in result.items():
            if service_data:
                formatted_result[service_type] = {
                    'name': service_data['name'],
                    'distance': service_data['distance'],
                    'phone': service_data['phone'],
                    'address': service_data['address']
                }
            else:
                formatted_result[service_type] = None
        
        return jsonify(formatted_result)
    except Exception as e:
        logging.error(f"Error finding nearest services: {str(e)}")
        return jsonify({'error': 'Failed to find nearest services'}), 500

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distance = R * c
    return round(distance, 2)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logging.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Set Flask environment
    os.environ['FLASK_ENV'] = 'development'
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5001))
    print(f"Starting Flask application on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
