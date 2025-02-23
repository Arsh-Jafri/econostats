from flask import Flask, render_template, make_response, jsonify, request
import pandas as pd
from visualizations import create_dashboard_components, create_combined_plot, filter_dataframe
from validate_data import load_and_validate_dataset
import os
from werkzeug.utils import secure_filename
from fred_api import FredData

app = Flask(__name__, static_url_path='/static', static_folder='static')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize FRED API
fred = FredData()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_all_datasets():
    """Modified to use FRED API"""
    data = fred.get_all_indicators()
    return data.get('CPIAUCSL'), data.get('PSAVERT'), data.get('PCEC')

@app.route('/')
def index():
    fred_data = FredData()
    indicators = fred_data.get_indicator_info()
    data = fred_data.get_all_indicators()
    
    plots_data, tables_html = create_dashboard_components(data)
    combined_plot = create_combined_plot(data)
    
    return render_template('index.html',
                         plots=plots_data,
                         tables=tables_html,
                         combined_plot=combined_plot.to_dict(),
                         indicators=indicators)

@app.route('/update_dashboard', methods=['POST'])
def update_dashboard():
    try:
        filters = request.json
        fred_data = FredData()
        all_data = fred_data.get_all_indicators()
        
        # Apply date filtering
        start_date = filters['dateRange']['start']
        end_date = filters['dateRange']['end']
        
        filtered_data = {}
        
        # Filter each selected indicator
        for indicator_id in filters['indicators']:
            if filters['indicators'][indicator_id]:  # If indicator is selected
                df = all_data.get(indicator_id)
                if df is not None:
                    filtered_data[indicator_id] = filter_dataframe(df, start_date, end_date)
        
        # Create plots and tables
        plots_data, tables_html = create_dashboard_components(filtered_data)
        
        # Create combined plot
        combined_plot = create_combined_plot(filtered_data)
        
        return jsonify({
            'plots': plots_data,
            'tables': tables_html,
            'combined_plot': combined_plot.to_dict()
        })
        
    except Exception as e:
        print(f"Error in update_dashboard: {str(e)}")  # Server-side logging
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print("Upload request received")
        if 'file' not in request.files:
            print("No file in request")
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        dataset_name = request.form.get('name')
        
        print(f"File name: {file.filename}")
        print(f"Dataset name: {dataset_name}")
        
        if file.filename == '':
            print("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            print("Invalid file type")
            return jsonify({'error': 'Invalid file type. Please upload a CSV file'}), 400
            
        if not dataset_name:
            print("No dataset name provided")
            return jsonify({'error': 'Please provide a name for the dataset'}), 400
        
        # Secure the filename using the custom name
        filename = secure_filename(f"{dataset_name}.csv")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Target filepath: {filepath}")
        
        # Check if file already exists
        if os.path.exists(filepath):
            print("File already exists")
            return jsonify({'error': 'A dataset with this name already exists'}), 400
        
        # Read the CSV data first to validate
        try:
            print("Reading CSV data")
            df = pd.read_csv(file)
            print("CSV data shape:", df.shape)
            
            # Basic validation
            if len(df.columns) < 2:
                print("Invalid number of columns")
                raise ValueError("CSV must have at least 2 columns (date and value)")
            
            # Try to parse dates from the first column
            print("Parsing dates")
            df.set_index(pd.to_datetime(df.iloc[:, 0]), inplace=True)
            df = df.iloc[:, 0]  # Take only the first data column
            df = pd.DataFrame(df)
            df.columns = [dataset_name]
            
            # Save the processed file
            print("Saving processed file")
            df.to_csv(filepath)
            
            # Add to FredData instance
            print("Adding to FredData instance")
            fred.add_custom_dataset(dataset_name, df)
            
            print("Upload successful")
            return jsonify({
                'message': 'File uploaded successfully',
                'name': dataset_name,
                'description': dataset_name
            }), 200
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 400
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/search_series', methods=['POST'])
def search_series():
    """New endpoint to search for available series"""
    try:
        search_text = request.json.get('search')
        results = fred.search_series(search_text)
        
        if results is None:
            return jsonify({'error': 'Search failed'}), 500
            
        # Format results for display
        formatted_results = []
        for result in results:
            formatted_results.append({
                'id': result.id,
                'title': result.title,
                'frequency': result.frequency,
                'units': result.units,
                'notes': result.notes
            })
            
        return jsonify({'results': formatted_results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fetch_series', methods=['POST'])
def fetch_series():
    """New endpoint to fetch a specific series"""
    try:
        series_id = request.json.get('series_id')
        data = fred.get_series_data(series_id)
        
        if data is None:
            return jsonify({'error': 'Failed to fetch series'}), 500
            
        return jsonify({
            'data': data.to_dict(orient='records'),
            'series_id': series_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002) 