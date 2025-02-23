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
        'CPIAUCSL': 'Consumer Price Index: All Items (CPIAUCSL)',
        'PSAVERT': 'Personal Savings Rate (PSAVERT)',
        'PCEC': 'Personal Consumption Expenditures (PCEC)',
        'GDPC1': 'Real Gross Domestic Product (GDPC1)',
        'UNRATE': 'Civilian Unemployment Rate (UNRATE)',
        'FEDFUNDS': 'Effective Federal Funds Rate (FEDFUNDS)',
        'M2SL': 'M2 Money Stock (M2SL)',
        'GS10': '10-Year Treasury Rate (GS10)',
        'INDPRO': 'Industrial Production Index (INDPRO)',
        'CSUSHPINSA': 'Case-Shiller Home Price Index (CSUSHPINSA)',
        'RRSFS': 'Retail and Food Services Sales (RRSFS)',
        'UMCSENT': 'Consumer Sentiment Index (UMCSENT)',
        'CPILFESL': 'Core Consumer Price Index (CPILFESL)'
    }
    
    def __init__(self, api_key=None):
        # Get API key from environment variable if not provided
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        if not self.api_key:
            raise ValueError("FRED API key not found. Set FRED_API_KEY environment variable.")
        
        self.fred = Fred(api_key=self.api_key)
        self._cache = {}  # Memory cache for current session
    
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
        """
        Fetch all economic indicators with rate limiting
        """
        data = {}
        for series_id in self.INDICATORS:
            data[series_id] = self.get_series_data(series_id)
            
        return data
    
    def get_indicator_info(self, series_id=None):
        """
        Get information about indicators
        """
        if series_id:
            return {
                'id': series_id,
                'description': self.INDICATORS.get(series_id, 'Unknown indicator')
            }
        return self.INDICATORS
    
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