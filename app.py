from flask import Flask, render_template, make_response, jsonify, request
import pandas as pd
from visualizations import create_dashboard_components, create_combined_plot, filter_dataframe
from validate_data import load_and_validate_dataset

app = Flask(__name__)

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
    
    plots_html, tables_html = create_dashboard_components(
        cpi_df, savings_df, consumption_df
    )
    
    combined_plot = create_combined_plot(
        cpi_df, savings_df, consumption_df
    ).to_html(full_html=False, include_plotlyjs=True)
    
    response = make_response(render_template('index.html',
                         plots=plots_html,
                         tables=tables_html,
                         combined_plot=combined_plot))
    response.headers['Cache-Control'] = 'public, max-age=300'
    return response

@app.route('/update_dashboard', methods=['POST'])
def update_dashboard():
    filters = request.json
    cpi_df, savings_df, consumption_df = load_all_datasets()
    
    # Apply date filtering
    start_date = filters['dateRange']['start']
    end_date = filters['dateRange']['end']
    
    if filters['indicators']['cpi']:
        cpi_df = filter_dataframe(cpi_df, start_date, end_date)
    else:
        cpi_df = None
        
    if filters['indicators']['savings']:
        savings_df = filter_dataframe(savings_df, start_date, end_date)
    else:
        savings_df = None
        
    if filters['indicators']['consumption']:
        consumption_df = filter_dataframe(consumption_df, start_date, end_date)
    else:
        consumption_df = None
    
    # Create plots and tables
    plots_html, tables_html = create_dashboard_components(
        cpi_df, savings_df, consumption_df
    )
    
    combined_plot = create_combined_plot(
        cpi_df, savings_df, consumption_df
    )
    
    return jsonify({
        'plots': plots_html,
        'tables': tables_html,
        'combined_plot': combined_plot.to_dict()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001) 