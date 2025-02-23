import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from fredapi import Fred
from fred_api import FredData

# Initialize Fred API
fred = Fred(api_key='YOUR_API_KEY')

def create_time_series_plot(df, title, y_label):
    """
    Create an interactive time series plot using Plotly
    """
    # Get the column name from the dataframe
    value_col = df.columns[0]
    
    # Convert dates to strings for JSON serialization
    x_data = df.index.strftime('%Y-%m-%d').tolist()
    y_data = df[value_col].tolist()
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_data,
            y=y_data,
            name=y_label,
            line=dict(color='#2c3e50', width=2)
        )
    )
    
    # Customize the layout with Rubik font
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(
                family='Rubik',
                size=20,
                color='#1E1E1E'
            )
        ),
        template='plotly_white',
        hovermode='x unified',
        height=400,
        margin=dict(l=40, r=20, t=60, b=80),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(
                family='Rubik',
                size=12
            )
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.5)',
            tickfont=dict(family='Rubik'),
            title_font=dict(family='Rubik', color='#1E1E1E')
        ),
        yaxis=dict(
            title=y_label,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.5)',
            tickfont=dict(family='Rubik'),
            title_font=dict(family='Rubik', color='#1E1E1E')
        ),
        font=dict(family='Rubik'),
        paper_bgcolor='#FCFCFC',  # Container background
        plot_bgcolor='#FCFCFC'    # Chart background
    )
    
    # Enhance the hover information
    fig.update_traces(
        hovertemplate=f"Date: %{{x}}<br>{y_label}: %{{y:.2f}}<extra></extra>"
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

def create_dashboard_components(data_dict):
    """
    Create all visualization components for the dashboard
    """
    plots_data = {}
    tables_html = {}
    
    # Create plots and tables for each available indicator
    for indicator_id, df in data_dict.items():
        if df is not None:
            # Get description from FredData.INDICATORS
            description = FredData.INDICATORS.get(indicator_id, indicator_id)
            
            # Create plot
            plot = create_time_series_plot(
                df,
                description,
                description
            )
            
            # Convert NaN to None in plot data for JSON serialization
            plot_dict = plot.to_dict()
            for trace in plot_dict.get('data', []):
                if 'y' in trace:
                    trace['y'] = [None if pd.isna(y) else y for y in trace['y']]
            
            plots_data[indicator_id] = plot_dict
            
            # Create summary table
            tables_html[indicator_id] = create_summary_table(df)
    
    return plots_data, tables_html

def smooth_series(series, window=5):
    """
    Smooth a series using a moving average
    """
    return pd.Series(series).rolling(window=window, center=True, min_periods=1).mean()

def create_combined_plot(data_dict, smoothing=5):
    """
    Create a combined plot with all indicators (normalized)
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Modern color palette
    colors = {
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
    }
    
    # Normalize each series (0-100 scale) without smoothing
    def normalize_series(series):
        series = series.dropna()
        if len(series) == 0 or series.max() == series.min():
            return series
        normalized = (100 * (series - series.min()) / (series.max() - series.min()))
        return normalized.tolist()
    
    # Add traces for each available indicator
    for indicator_id, df in data_dict.items():
        if df is not None:
            y_data = normalize_series(df[indicator_id])
            y_data = [None if pd.isna(y) else y for y in y_data]
            
            fig.add_trace(
                go.Scatter(
                    x=df.index.strftime('%Y-%m-%d').tolist(),
                    y=y_data,
                    name=FredData.INDICATORS.get(indicator_id, indicator_id),
                    line=dict(
                        color=colors.get(indicator_id, 'black'),
                        shape='spline',  # Add curve smoothing
                        smoothing=1.3    # Adjust smoothing factor
                    )
                ),
                secondary_y=False
            )
    
    # Update layout with Rubik font
    fig.update_layout(
        title=dict(
            text="Combined Economic Indicators (Normalized)",
            x=0.5,
            font=dict(
                family='Rubik',
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
                family='Rubik',
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
            family='Rubik'
        )
    )
    
    # Update axes labels with Rubik font
    fig.update_yaxes(
        title_text="Normalized Scale (0-100)",
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(211,211,211,0.5)',
        secondary_y=False,
        tickfont=dict(family='Rubik'),
        title_font=dict(family='Rubik', color='#1E1E1E')
    )
    
    return fig

def filter_dataframe(df, start_date, end_date):
    """
    Filter a dataframe based on date range
    """
    if df is None:
        return None
    
    mask = (df.index >= start_date) & (df.index <= end_date)
    return df.loc[mask] 