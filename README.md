<p align="center">
  <img src="static/logo-white.png" alt="Econostats Logo" width="600"/>
</p>

<h1 align="center"><a href="https://econostats.co">econostats.co</a></h1>

## About Econostats

Econostats is a dynamic web application designed to visualize and analyze key economic indicators in real-time. The platform provides an intuitive interface for tracking various economic metrics, helping users understand economic trends and make data-driven decisions.

## Features

- **Real-time Data**: Integration with FRED (Federal Reserve Economic Data) API for up-to-date economic indicators
- **Interactive Visualizations**: Dynamic charts with zoom, pan, and hover capabilities
- **Customizable Dashboard**: Select and combine different economic indicators
- **Data Analysis Tools**: 
  - Curve smoothing for trend analysis
  - Line thickness adjustment for better visualization
  - Date range selection
  - Normalized data comparison
- **Responsive Design**: Optimized for desktop viewing with mobile-friendly warning system
- **Dark/Light Mode**: Toggle between themes for comfortable viewing

## Tech Stack

### Frontend
- HTML5/CSS3
- JavaScript
- Plotly.js for interactive charts
- Inter Tight font family for modern typography

### Backend
- Python 3.11
- Flask 3.0.0 web framework
- Pandas for data manipulation
- NumPy for numerical computations
- FRED API for economic data
- Gunicorn WSGI server

### Deployment
- AWS Elastic Beanstalk
- Apache web server
- Git version control

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-username/econostats.git
cd econostats
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Create a `.env` file
- Add your FRED API key: `FRED_API_KEY=your_api_key_here`

5. Run the application:
```bash
python app.py
```

## Project Structure
```
econostats/
├── app.py                 # Main Flask application
├── fred_api.py           # FRED API integration
├── visualizations.py     # Chart creation and styling
├── validate_data.py      # Data validation utilities
├── static/              # Static assets (images, etc.)
├── templates/           # HTML templates
└── requirements.txt     # Python dependencies
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by [Arsh Jafri](https://github.com/Arsh-Jafri)

## Acknowledgments

- Federal Reserve Economic Data (FRED) for providing the economic data API
- AWS for hosting services
- All contributors and supporters of the project