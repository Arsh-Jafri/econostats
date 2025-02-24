<p align="center">
  <img src="static/logo-white.png" alt="Econostats Logo" width="500"/>
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

## Data Management

- **FRED API**: Real-time economic data fetching via REST API
- **Pandas DataFrames**: In-memory data processing
- **CSV Storage**: Local storage for custom uploaded datasets
- **Requests Cache**: SQLite-based caching for API responses

## API Endpoints

### Data Management
- `GET /`: Main dashboard view
- `POST /update_dashboard`: Update dashboard with selected indicators
- `POST /upload`: Upload custom dataset
- `POST /delete_dataset`: Remove custom dataset

### FRED Integration
- `POST /search_series`: Search available FRED series
- `POST /fetch_series`: Fetch specific FRED series data

### Features
- Real-time data fetching from FRED API
- Custom dataset upload and management
- Dashboard state management
- Series search functionality

## Tech Stack

### Frontend
- HTML5/CSS3
- JavaScript
- Plotly.js for interactive charts
- Inter Tight font family

### Backend
- Python 3.11
- Flask 3.0.0 web framework
- Pandas for data manipulation
- NumPy for numerical computations
- FRED API for economic data
- Requests-cache for API response caching
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

## Creator

Created by [Arsh Jafri](https://github.com/Arsh-Jafri)
- [LinkedIn](https://www.linkedin.com/in/arshjafri/)
- [GitHub](https://github.com/Arsh-Jafri)

## Acknowledgments

- Federal Reserve Economic Data (FRED) for providing the economic data API
- AWS for hosting services
- All contributors and supporters of the project
