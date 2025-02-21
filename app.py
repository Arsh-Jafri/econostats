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
    cpi_df, _ = load_and_validate_dataset('CPIAUCSL.csv')
    savings_df, _ = load_and_validate_dataset('PSAVERT.csv')
    consumption_df, _ = load_and_validate_dataset('PCEC.csv')
    return cpi_df, savings_df, consumption_df

@app.route('/')
def index():
    cpi_df, savings_df, consumption_df = load_all_datasets()
    
    if any(df is None for df in [cpi_df, savings_df, consumption_df]):
        return "Error: Failed to load one or more datasets", 500
    
    plots_data, tables_html = create_dashboard_components(
        cpi_df, savings_df, consumption_df
    )
    
    combined_plot = create_combined_plot(
        cpi_df, savings_df, consumption_df
    )
    
    return render_template('index.html',
                         plots=plots_data,
                         tables=tables_html,
                         combined_plot=combined_plot.to_dict())

@app.route('/update_dashboard', methods=['POST'])
def update_dashboard():
    try:
        filters = request.json
        cpi_df, savings_df, consumption_df = load_all_datasets()
        
        # Apply date filtering
        start_date = filters['dateRange']['start']
        end_date = filters['dateRange']['end']
        
        filtered_data = {}
        
        if filters['indicators']['cpi']:
            filtered_data['cpi'] = filter_dataframe(cpi_df, start_date, end_date)
        else:
            filtered_data['cpi'] = None
            
        if filters['indicators']['savings']:
            filtered_data['savings'] = filter_dataframe(savings_df, start_date, end_date)
        else:
            filtered_data['savings'] = None
            
        if filters['indicators']['consumption']:
            filtered_data['consumption'] = filter_dataframe(consumption_df, start_date, end_date)
        else:
            filtered_data['consumption'] = None
        
        # Create plots and tables
        plots_html, tables_html = create_dashboard_components(
            filtered_data['cpi'], 
            filtered_data['savings'], 
            filtered_data['consumption']
        )
        
        # Create combined plot
        combined_plot = create_combined_plot(
            filtered_data['cpi'], 
            filtered_data['savings'], 
            filtered_data['consumption']
        )
        
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
        data_type = request.form.get('type')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a CSV file'}), 400
            
        if data_type not in ['cpi', 'savings', 'consumption']:
            return jsonify({'error': 'Invalid data type'}), 400
        
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate and process the uploaded file
        try:
            df = pd.read_csv(filepath)
            
            # Basic validation
            if len(df.columns) < 2:
                raise ValueError("CSV must have at least 2 columns (date and value)")
            
            # Try to parse dates
            df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
            
            # Save with standardized name based on type
            type_to_filename = {
                'cpi': 'CPIAUCSL.csv',
                'savings': 'PSAVERT.csv',
                'consumption': 'PCEC.csv'
            }
            
            final_path = os.path.join(app.config['UPLOAD_FOLDER'], type_to_filename[data_type])
            df.to_csv(final_path, index=False)
            
            return jsonify({'message': 'File uploaded successfully'}), 200
            
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 