import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from fredapi import Fred
from fred_api import FredData

# Initialize Fred API
fred = Fred(api_key='YOUR_API_KEY')

# Add these color palettes at the top of the file
THEME_COLORS = {
    'default': {
        'CPIAUCSL': '#2c3e50',  # Dark blue
        'PSAVERT': '#27ae60',   # Green
        'PCEC': '#c0392b',      # Red
        'GDPC1': '#8e44ad',     # Purple
        'UNRATE': '#d35400',    # Orange
        'FEDFUNDS': '#795548',  # Brown
        'M2SL': '#e91e63',      # Pink
        'GS10': '#607d8b',      # Gray
        'INDPRO': '#00bcd4',    # Cyan
        'CSUSHPINSA': '#9c27b0', # Magenta
        'RRSFS': '#827717',     # Olive
        'UMCSENT': '#009688',   # Teal
        'CPILFESL': '#1a237e'   # Navy
    },
    'distinct': {
        'CPIAUCSL': '#FF6B6B',  # Coral Red
        'PSAVERT': '#4ECDC4',   # Turquoise
        'PCEC': '#45B7D1',      # Sky Blue
        'GDPC1': '#96CEB4',     # Sage
        'UNRATE': '#FFEEAD',    # Cream
        'FEDFUNDS': '#D4A5A5',  # Dusty Rose
        'M2SL': '#9B59B6',      # Purple
        'GS10': '#3498DB',      # Blue
        'INDPRO': '#F1C40F',    # Yellow
        'CSUSHPINSA': '#E74C3C', # Red
        'RRSFS': '#2ECC71',     # Green
        'UMCSENT': '#34495E',   # Navy
        'CPILFESL': '#E67E22'   # Orange
    },
    'pastel': {
        'CPIAUCSL': '#FFB3BA',  # Pastel Red
        'PSAVERT': '#BAFFC9',   # Pastel Green
        'PCEC': '#BAE1FF',      # Pastel Blue
        'GDPC1': '#FFFFBA',     # Pastel Yellow
        'UNRATE': '#FFB3F7',    # Pastel Pink
        'FEDFUNDS': '#B3FFF7',  # Pastel Turquoise
        'M2SL': '#FFC9DE',      # Light Pink
        'GS10': '#C9BAFF',      # Pastel Purple
        'INDPRO': '#FFE4BA',    # Pastel Orange
        'CSUSHPINSA': '#BAFFC9', # Light Green
        'RRSFS': '#BAF7FF',     # Light Blue
        'UMCSENT': '#FFBAED',   # Pink
        'CPILFESL': '#BAFFE4'   # Mint
    },
    'techno': {
        'CPIAUCSL': '#00FF41',  # Matrix Green
        'PSAVERT': '#0FF0FC',   # Cyan
        'PCEC': '#FC0FC0',      # Neon Pink
        'GDPC1': '#FFA400',     # Neon Orange
        'UNRATE': '#FF0F7B',    # Hot Pink
        'FEDFUNDS': '#4D4DFF',  # Electric Blue
        'M2SL': '#BC13FE',      # Purple
        'GS10': '#1EFF00',      # Lime
        'INDPRO': '#00FFFF',    # Aqua
        'CSUSHPINSA': '#FF1493', # Deep Pink
        'RRSFS': '#7FFF00',     # Chartreuse
        'UMCSENT': '#00BFFF',   # Deep Sky Blue
        'CPILFESL': '#FF4500'   # Orange Red
    },
    'organic': {
        'CPIAUCSL': '#8B4513',  # Saddle Brown
        'PSAVERT': '#556B2F',   # Olive Green
        'PCEC': '#2F4F4F',      # Dark Slate Gray
        'GDPC1': '#8B8B00',     # Yellow Green
        'UNRATE': '#CD853F',    # Peru
        'FEDFUNDS': '#6B8E23',  # Olive Drab
        'M2SL': '#BC8F8F',      # Rosy Brown
        'GS10': '#4A766E',      # Ocean Green
        'INDPRO': '#8B7355',    # Brown
        'CSUSHPINSA': '#698B22', # Dark Olive Green
        'RRSFS': '#4F4F2F',     # Dark Olive
        'UMCSENT': '#548B54',   # Medium Sea Green
        'CPILFESL': '#8B7765'   # Light Wood
    }
}

def create_time_series_plot(df, title, y_label, indicator_id, theme_colors):
    """
    Create an interactive time series plot using Plotly
    """
    print(f"\nCreating plot for: {indicator_id}")
    print(f"Data type: {type(df)}")
    print(f"Columns: {df.columns if isinstance(df, pd.DataFrame) else 'Not a DataFrame'}")
    print(f"Sample data:\n{df.head()}")
    
    # Get the color for this indicator from the theme
    line_color = theme_colors.get(indicator_id, '#000000')
    if 'custom' in theme_colors and indicator_id in theme_colors['custom']:
        line_color = theme_colors['custom'][indicator_id]
        print(f"Using custom color: {line_color}")
    
    # Convert DataFrame to series if needed
    if isinstance(df, pd.DataFrame):
        series = df.iloc[:, 0] if len(df.columns) > 0 else df
    else:
        series = df
    
    print(f"Final series data:\n{series.head()}")
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df.index.strftime('%Y-%m-%d').tolist(),
            y=series.values.tolist(),
            name=y_label,
            line=dict(
                color=line_color,
                shape='spline',
                smoothing=1.3
            )
        )
    )
    
    # Simplified layout with less redundant information
    fig.update_layout(
        title=None,  # Remove title since it's already in the card header
        template='plotly_white',
        hovermode='x unified',
        height=300,  # Reduced height
        margin=dict(l=40, r=20, t=20, b=20),  # Reduced margins
        showlegend=False,  # Remove legend since it's redundant
        xaxis=dict(
            title=None,  # Remove x-axis title since it's always Date
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.5)',
            tickfont=dict(
                family='Inter Tight',
                size=10
            )
        ),
        yaxis=dict(
            title=None,  # Remove y-axis title since it's clear from context
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.5)',
            tickfont=dict(
                family='Inter Tight',
                size=10
            )
        ),
        font=dict(family='Inter Tight'),
        paper_bgcolor='#FCFCFC',
        plot_bgcolor='#FCFCFC'
    )
    
    # Fix the hover template formatting - escape the % characters
    fig.update_traces(
        hovertemplate=f"{y_label}: %{{y:,.2f}}<br>Date: %{{x}}<extra></extra>"  # Double curly braces to escape
    )
    
    return fig

def create_summary_table(df):
    """
    Create an HTML table with summary statistics
    """
    # Get the latest value
    current_value = df.iloc[-1].values[0]
    
    # Calculate YTD change (from start of current year)
    current_year = pd.Timestamp.now().year
    year_start = pd.Timestamp(f"{current_year}-01-01")
    ytd_value = df.loc[df.index >= year_start].iloc[0].values[0] if len(df.loc[df.index >= year_start]) > 0 else None
    ytd_change = current_value - ytd_value if ytd_value is not None else None
    
    # Calculate YOY change
    year_ago = pd.Timestamp.now() - pd.DateOffset(years=1)
    yoy_value = df.loc[df.index <= year_ago].iloc[-1].values[0] if len(df.loc[df.index <= year_ago]) > 0 else None
    yoy_change = current_value - yoy_value if yoy_value is not None else None
    
    # Calculate other statistics
    all_time_high = df.values.max()
    all_time_low = df.values.min()
    average = df.values.mean()
    
    # Create summary DataFrame
    summary = pd.DataFrame({
        'Statistic': [
            'Current Value',
            'YTD Change',
            'YOY Change',
            'All-Time High',
            'All-Time Low',
            'Average'
        ],
        'Value': [
            f"{current_value:.2f}",
            f"{ytd_change:.2f}" if ytd_change is not None else "N/A",
            f"{yoy_change:.2f}" if yoy_change is not None else "N/A",
            f"{all_time_high:.2f}",
            f"{all_time_low:.2f}",
            f"{average:.2f}"
        ]
    })
    
    # Convert to HTML table
    table_html = """
    <table class="stat-table">
        <tr>
            <th>Statistic</th>
            <th>Value</th>
        </tr>
    """
    
    for _, row in summary.iterrows():
        table_html += f"""
        <tr>
            <td>{row['Statistic']}</td>
            <td>{row['Value']}</td>
        </tr>
        """
    
    table_html += "</table>"
    
    return table_html

def create_dashboard_components(data_dict, theme='default'):
    """
    Create all visualization components for the dashboard
    """
    plots_data = {}
    tables_html = {}
    
    # Create combined plot first to get the colors
    combined_plot, theme_colors = create_combined_plot(data_dict, theme=theme)
    
    # Create plots and tables for each available indicator
    for indicator_id, df in data_dict.items():
        if df is not None:
            # Get description from FredData.INDICATORS
            description = FredData.INDICATORS.get(indicator_id, indicator_id)
            
            # Create individual plot with matching colors
            plot = create_time_series_plot(
                df,
                description,
                description,
                indicator_id,
                theme_colors
            )
            
            # Store plot data
            plots_data[indicator_id] = plot.to_dict()
            
            # Create summary table
            tables_html[indicator_id] = create_summary_table(df)
    
    return combined_plot.to_dict(), plots_data, tables_html

def smooth_series(series, window=5):
    """
    Smooth a series using a moving average
    """
    return pd.Series(series).rolling(window=window, center=True, min_periods=1).mean()

def normalize_series(series):
    """
    Normalize a series to 0-100 scale
    """
    # Convert numpy array to pandas Series
    series = pd.Series(series)
    series = series.dropna()
    
    if len(series) == 0 or series.max() == series.min():
        return series
    
    normalized = (100 * (series - series.min()) / (series.max() - series.min()))
    return normalized.tolist()

def create_combined_plot(data_dict, smoothing=5, theme='default'):
    """
    Create a combined plot with all indicators (normalized)
    """
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    # Get colors from the selected theme
    colors = THEME_COLORS.get(theme, THEME_COLORS['default'])
    
    # Add traces for each available indicator
    for indicator_id, df in data_dict.items():
        if df is not None:
            # Convert to pandas Series if it's a numpy array
            y_data = normalize_series(df.values.flatten() if hasattr(df.values, 'flatten') else df.values)
            
            fig.add_trace(
                go.Scatter(
                    x=df.index.strftime('%Y-%m-%d').tolist(),
                    y=y_data,
                    name=FredData.INDICATORS.get(indicator_id, indicator_id),
                    line=dict(
                        color=colors.get(indicator_id, 'black'),
                        shape='spline',
                        smoothing=1.3
                    )
                ),
                secondary_y=False
            )
    
    # Update layout with Inter Tight font
    fig.update_layout(
        title=dict(
            text="Combined Economic Indicators (Normalized)",
            x=0.5,
            font=dict(
                family='Inter Tight',
                size=24,
                color='#1E1E1E'
            )
        ),
        template='plotly_white',
        hovermode='x unified',
        height=550,
        margin=dict(
            l=40,
            r=20,
            t=60,
            b=150
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(
                family='Inter Tight',
                size=12,
                color='#363636'
            ),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1
        ),
        paper_bgcolor='#FCFCFC',  # Container background
        plot_bgcolor='#FCFCFC',   # Chart background
        font=dict(
            family='Inter Tight'
        )
    )
    
    # Update axes labels with Inter Tight font
    fig.update_yaxes(
        title_text="Normalized Scale (0-100)",
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(211,211,211,0.5)',
        secondary_y=False,
        tickfont=dict(family='Inter Tight'),
        title_font=dict(family='Inter Tight', color='#1E1E1E')
    )
    
    return fig, colors  # Return the colors used for individual plots

def filter_dataframe(df, start_date, end_date):
    """
    Filter a dataframe based on date range
    """
    if df is None:
        return None
    
    mask = (df.index >= start_date) & (df.index <= end_date)
    return df.loc[mask] 