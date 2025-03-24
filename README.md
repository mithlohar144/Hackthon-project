# Universal Translator & Emergency Services Platform

A web application that combines real-time language translation with emergency services location features.

## Features

### Universal Translator
- Real-time text translation between multiple languages
- Support for 11 languages including:
  - English
  - Spanish
  - French
  - German
  - Italian
  - Portuguese
  - Russian
  - Japanese
  - Korean
  - Chinese
  - Hindi
- Automatic language detection
- Language swap functionality
- Clean and intuitive interface

### Emergency Services
- One-click emergency service requests
- Automatic location detection
- Real-time nearest emergency services using OpenStreetMap
- Distance calculation to nearest services
- Support for:
  - Police Stations
  - Hospitals
  - Fire Stations
- Detailed service information including addresses

## Technical Stack

- Backend: Python/Flask
- Frontend: HTML5, CSS3, JavaScript
- APIs: Google Translate, OpenStreetMap
- UI Framework: Bootstrap 5
- Icons: Font Awesome

## Installation

1. Clone the repository:
```bash
git clone https://github.com/<yourusername>/universal-translator-emergency.git
cd universal-translator-emergency
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5001
```

## Dependencies

- Flask
- Flask-CORS
- deep-translator
- python-dotenv
- requests

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Translate API for translation services
- OpenStreetMap for emergency services data
- Bootstrap for the UI framework
- Font Awesome for icons

## GitHub Repository

This project is available on GitHub at:

https://github.com/mithlohar144/universal-translator-emergency
