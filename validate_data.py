import pandas as pd
import numpy as np
from datetime import datetime
import os

def determine_frequency(df):
    """
    Determine the frequency of the time series data
    """
    if len(df) < 2:
        return "Unknown"
    
    # Calculate the most common time difference between consecutive dates
    diff = df.index.to_series().diff().mode()[0]
    days = diff.days
    
    if days >= 88 and days <= 92:  # Approximately 3 months
        return "Quarterly"
    elif days >= 28 and days <= 31:
        return "Monthly"
    else:
        return f"Unknown ({days} days)"

def load_and_validate_dataset(file_path):
    """
    Load and perform basic validation on a CSV dataset.
    Returns the cleaned DataFrame and a validation report.
    """
    # Add input validation
    if not file_path.endswith('.csv'):
        raise ValueError("File must be a CSV")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Assuming first column is the date
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Set date as index
        df.set_index(date_col, inplace=True)
        
        # Basic cleaning
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Additional validation checks
        value_col = df.columns[0]  # Get the main value column
        report = {
            "filename": file_path,
            "total_rows": len(df),
            "missing_values": df.isnull().sum().to_dict(),
            "date_range": f"{df.index.min()} to {df.index.max()}",
            "columns": list(df.columns),
            "value_range": f"{df[value_col].min():.2f} to {df[value_col].max():.2f}",
            "frequency": determine_frequency(df),
            "time_span_years": f"{(df.index.max() - df.index.min()).days / 365.25:.1f}"
        }
        
        return df, report
        
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None, {"error": str(e)}

def print_dataset_summary(df, report, dataset_name):
    """
    Print a formatted summary of the dataset
    """
    print(f"\n{'='*50}")
    print(f"Validating {dataset_name}...")
    print(f"{'='*50}")
    
    if df is not None:
        print("\nSummary Statistics:")
        print(df.describe())
        
        print("\nFirst few rows:")
        print(df.head())
        
        print("\nValidation Report:")
        for key, value in report.items():
            print(f"{key}: {value}")
    else:
        print(f"Failed to load {dataset_name}")

def main():
    # List of all datasets to load
    datasets = [
        "CPIAUCSL.csv",
        "PSAVERT.csv",
        "PCEC.csv"
    ]
    
    loaded_data = {}
    validation_reports = {}
    
    for dataset in datasets:
        try:
            df, report = load_and_validate_dataset(dataset)
            loaded_data[dataset] = df
            validation_reports[dataset] = report
            print_dataset_summary(df, report, dataset)
        except FileNotFoundError:
            print(f"\nWarning: {dataset} not found in the current directory")
            continue

if __name__ == "__main__":
    main() 