import pandas as pd
import numpy as np
from datetime import datetime

def load_and_validate_dataset(file_path):
    """
    Load and perform basic validation on a CSV dataset.
    Returns the cleaned DataFrame and a validation report.
    """
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
        
        # Generate validation report
        report = {
            "filename": file_path,
            "total_rows": len(df),
            "missing_values": df.isnull().sum().to_dict(),
            "date_range": f"{df.index.min()} to {df.index.max()}",
            "columns": list(df.columns)
        }
        
        return df, report
        
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None, {"error": str(e)}

def main():
    # List of datasets to load
    datasets = ["CPIAUCSL.csv"]  # We'll add PSAVERT.csv and PCEC.csv when available
    
    loaded_data = {}
    validation_reports = {}
    
    for dataset in datasets:
        print(f"\nValidating {dataset}...")
        df, report = load_and_validate_dataset(dataset)
        
        if df is not None:
            loaded_data[dataset] = df
            validation_reports[dataset] = report
            
            # Print summary statistics
            print("\nSummary Statistics:")
            print(df.describe())
            
            print("\nFirst few rows:")
            print(df.head())
            
            print("\nValidation Report:")
            for key, value in report.items():
                print(f"{key}: {value}")
        else:
            print(f"Failed to load {dataset}")

if __name__ == "__main__":
    main() 