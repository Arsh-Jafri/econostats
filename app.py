from flask import Flask, render_template, make_response, jsonify, request
import pandas as pd
from visualizations import create_dashboard_components, create_combined_plot, filter_dataframe
from validate_data import load_and_validate_dataset
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_all_datasets():
    datasets = {}
    upload_dir = app.config['UPLOAD_FOLDER']
    
    # Load all CSV files from upload directory
    for filename in os.listdir(upload_dir):
        if filename.endswith('.csv'):
            name = os.path.splitext(filename)[0]
            df, _ = load_and_validate_dataset(os.path.join(upload_dir, filename))
            if df is not None:
                datasets[name] = df
    
    return datasets

@app.route('/')
def index():
    datasets = load_all_datasets()
    
    if not datasets:
        return "Error: No datasets available", 500
    
    plots_data, tables_html = create_dashboard_components(datasets)
    combined_plot = create_combined_plot(datasets)
    
    return render_template('index.html',
                         plots=plots_data,
                         tables=tables_html,
                         combined_plot=combined_plot.to_dict(),
                         datasets=list(datasets.keys()))

@app.route('/update_dashboard', methods=['POST'])
def update_dashboard():
    try:
        filters = request.json
        datasets = load_all_datasets()
        
        # Apply date filtering
        start_date = filters['dateRange']['start']
        end_date = filters['dateRange']['end']
        
        filtered_data = {}
        
        for name, df in datasets.items():
            if filters['indicators'][name]:
                filtered_data[name] = filter_dataframe(df, start_date, end_date)
            else:
                filtered_data[name] = None
        
        # Create plots and tables
        plots_html, tables_html = create_dashboard_components(filtered_data)
        
        # Create combined plot
        combined_plot = create_combined_plot(filtered_data)
        
        return jsonify({
            'plots': plots_html,
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
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        dataset_name = request.form.get('name')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a CSV file'}), 400
            
        if not dataset_name:
            return jsonify({'error': 'Dataset name is required'}), 400
        
        # Secure the filename using the provided name
        filename = secure_filename(f"{dataset_name}.csv")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file already exists
        if os.path.exists(filepath):
            return jsonify({'error': 'A dataset with this name already exists'}), 400
        
        file.save(filepath)
        
        # Validate and process the uploaded file
        try:
            df = pd.read_csv(filepath)
            
            # Basic validation
            if len(df.columns) < 2:
                os.remove(filepath)
                raise ValueError("CSV must have at least 2 columns (date and value)")
            
            # Try to parse dates
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
            
            # Save the processed file
            df.to_csv(filepath, index=False)
            
            return jsonify({
                'message': 'File uploaded successfully',
                'name': dataset_name
            }), 200
            
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002) 