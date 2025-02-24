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
    # Initialize FredData instance
    fred_data = FredData()
    data = fred_data.get_all_indicators()  # Changed from get_all_data() to match your API
    combined_plot, plots, tables = create_dashboard_components(data)
    return render_template('index.html', 
                         indicators=FredData.INDICATORS,
                         combined_plot=combined_plot,
                         plots=plots,
                         tables=tables)

@app.route('/update_dashboard', methods=['POST'])
def update_dashboard():
    try:
        filters = request.json
        fred_data = FredData()
        all_data = fred_data.get_all_indicators()
        
        # Get parameters
        smoothing = filters.get('smoothing', 5)
        theme = filters.get('theme', 'default')
        
        # Apply date filtering
        start_date = filters['dateRange']['start']
        end_date = filters['dateRange']['end']
        
        filtered_data = {}
        for indicator_id in filters['indicators']:
            if filters['indicators'][indicator_id]:
                df = all_data.get(indicator_id)
                if df is not None:
                    filtered_data[indicator_id] = filter_dataframe(df, start_date, end_date)
        
        # Create plots with theme
        combined_plot, plots, tables = create_dashboard_components(filtered_data, theme=theme)
        
        return jsonify({
            'plots': plots,
            'tables': tables,
            'combined_plot': combined_plot
        })
        
    except Exception as e:
        print(f"Error in update_dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        dataset_name = request.form.get('name')
        
        if file.filename == '':
            print("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            print("Invalid file type")
            return jsonify({'error': 'Invalid file type. Please upload a CSV file'}), 400
            
        if not dataset_name:
            print("No dataset name provided")
            return jsonify({'error': 'Please provide a name for the dataset'}), 400
        
        filename = secure_filename(f"{dataset_name}.csv")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Read the CSV data first to validate
        try:
            df = pd.read_csv(file)
            
            # Basic validation
            if len(df.columns) < 2:
                raise ValueError("CSV must have at least 2 columns (date and value)")
            
            # Set the date column as index
            date_col = df.columns[0]
            value_col = df.columns[1]
            
            print(f"Original columns: {df.columns}")
            print(f"Data before processing:\n{df.head()}")
            
            df[date_col] = pd.to_datetime(df[date_col])
            df.set_index(date_col, inplace=True)
            
            # Keep only the value column and rename it
            df = df[[value_col]]
            df.columns = [dataset_name]
            
            print(f"Data after processing:\n{df.head()}")
            
            # Save the processed file
            df.to_csv(filepath)
            
            # Add to FredData instance
            fred.add_custom_dataset(dataset_name, df)
            
            # Verify data was added correctly
            print(f"Verifying data in FredData:\n{fred.custom_indicators[dataset_name]['data'].head()}")
            
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

@app.route('/delete_dataset', methods=['POST'])
def delete_dataset():
    try:
        dataset_name = request.json.get('dataset_name')
        if not dataset_name:
            return jsonify({'error': 'No dataset name provided'}), 400
            
        # Delete the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{dataset_name}.csv")
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Remove from FredData instance
        if hasattr(fred, 'custom_indicators'):
            fred.custom_indicators.pop(dataset_name, None)
            
        return jsonify({'message': 'Dataset deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002) 