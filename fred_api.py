from fredapi import Fred
import pandas as pd
from dotenv import load_dotenv
import os
import requests_cache
from datetime import timedelta

# Load environment variables
load_dotenv()

# Setup cache
requests_cache.install_cache(
    'fred_cache',
    backend='sqlite',
    expire_after=timedelta(hours=24)  # Cache for 24 hours
)

class FredData:
    # Dictionary of all indicators with their descriptions
    INDICATORS = {
        'CPIAUCSL': 'Consumer Price Index: All Items',
        'PSAVERT': 'Personal Savings Rate',
        'PCEC': 'Personal Consumption Expenditures',
        'GDPC1': 'Real Gross Domestic Product',
        'UNRATE': 'Civilian Unemployment Rate',
        'FEDFUNDS': 'Effective Federal Funds Rate',
        'M2SL': 'M2 Money Stock',
        'GS10': '10-Year Treasury Rate',
        'INDPRO': 'Industrial Production Index',
        'CSUSHPINSA': 'Case-Shiller Home Price Index',
        'RRSFS': 'Retail and Food Services Sales',
        'UMCSENT': 'Consumer Sentiment Index',
        'CPILFESL': 'Core Consumer Price Index'
    }
    
    def __init__(self, api_key=None):
        # Get API key from environment variable if not provided
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        if not self.api_key:
            raise ValueError("FRED API key not found. Set FRED_API_KEY environment variable.")
        
        self.fred = Fred(api_key=self.api_key)
        self._cache = {}  # Memory cache for current session
        self.custom_indicators = {}  # Store custom datasets
        self.load_custom_datasets()  # Load any existing custom datasets
    
    def load_custom_datasets(self):
        """Load custom datasets from the uploads folder"""
        upload_dir = 'uploads'
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename.endswith('.csv'):
                    try:
                        dataset_name = filename[:-4]  # Remove .csv extension
                        df = pd.read_csv(os.path.join(upload_dir, filename))
                        df.set_index(pd.to_datetime(df.iloc[:, 0]), inplace=True)
                        df.columns = [dataset_name]
                        self.custom_indicators[dataset_name] = {
                            'description': dataset_name,
                            'data': df
                        }
                    except Exception as e:
                        print(f"Error loading custom dataset {filename}: {str(e)}")

    def get_series_data(self, series_id):
        """
        Fetch data for a given series ID from FRED with caching
        """
        # Check memory cache first
        if series_id in self._cache:
            return self._cache[series_id]
        
        try:
            # Get the data (will use requests_cache)
            df = self.fred.get_series(series_id)
            
            # Convert to DataFrame with proper date index
            df = pd.DataFrame(df)
            df.index.name = 'observation_date'
            df.columns = [series_id]
            
            # Store in memory cache
            self._cache[series_id] = df
            
            return df
            
        except Exception as e:
            print(f"Error fetching {series_id}: {str(e)}")
            return None
    
    def get_all_indicators(self):
        """Get both FRED and custom indicators"""
        data = {}
        # Get FRED indicators
        for series_id in self.INDICATORS:
            data[series_id] = self.get_series_data(series_id)
        
        # Add custom indicators
        for dataset_name, dataset_info in self.custom_indicators.items():
            data[dataset_name] = dataset_info['data']
        
        return data
    
    def get_indicator_info(self, series_id=None):
        """Get information about all indicators including custom ones"""
        all_indicators = self.INDICATORS.copy()
        
        # Add custom indicators
        for name, info in self.custom_indicators.items():
            all_indicators[name] = info['description']
            
        if series_id:
            return {
                'id': series_id,
                'description': all_indicators.get(series_id, 'Unknown indicator')
            }
        return all_indicators
    
    def search_series(self, search_text):
        """
        Search for available series in FRED
        """
        try:
            results = self.fred.search(search_text)
            return results
        except Exception as e:
            print(f"Error searching: {str(e)}")
            return None
    
    def get_indicator_metadata(self, series_id):
        """
        Get detailed metadata for an indicator
        """
        try:
            return self.fred.get_series_info(series_id)
        except Exception as e:
            print(f"Error fetching metadata for {series_id}: {str(e)}")
            return None
    
    def clear_cache(self):
        """
        Clear both memory and disk cache
        """
        self._cache.clear()
        requests_cache.clear()

    def add_custom_dataset(self, name, df):
        """Add a new custom dataset"""
        self.custom_indicators[name] = {
            'description': name,
            'data': df
        } 