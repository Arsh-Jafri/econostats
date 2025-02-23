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
            line=dict(color='blue')
        )
    )
    
    # Customize the layout
    fig.update_layout(
        title=title,
        title_x=0.5,
        title_font_size=20,
        template='plotly_white',
        hovermode='x unified',
        height=400,
        margin=dict(l=40, r=20, t=60, b=80),  # Adjusted margins
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=-0.3,  # Position below the plot
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.5)'
        ),
        yaxis=dict(
            title=y_label,
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.5)'
        )
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
    # Calculate summary statistics
    summary = pd.DataFrame({
        'Statistic': [
            'Current Value',
            'Year-to-Date Change',
            'Year-over-Year Change',
            'All-Time High',
            'All-Time Low',
            'Average (All Time)'
        ],
        'Value': [
            f"{df.iloc[-1].values[0]:.2f}",
            f"{(df.iloc[-1].values[0] - df.iloc[-12].values[0]):.2f}",
            "N/A",
            f"{df.values.max():.2f}",
            f"{df.values.min():.2f}",
            f"{df.values.mean():.2f}"
        ]
    })
    
    # Convert to HTML with styling
    table_html = summary.to_html(
        classes=['table', 'table-striped', 'table-hover'],
        index=False,
        border=0
    )
    
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

def create_combined_plot(data_dict):
    """
    Create a combined plot with all indicators (normalized)
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Color map for different indicators
    colors = {
        'CPIAUCSL': 'blue',
        'PSAVERT': 'green',
        'PCEC': 'red',
        'GDPC1': 'purple',
        'UNRATE': 'orange',
        'FEDFUNDS': 'brown',
        'M2SL': 'pink',
        'GS10': 'gray',
        'INDPRO': 'cyan',
        'CSUSHPINSA': 'magenta',
        'RRSFS': 'olive',
        'UMCSENT': 'teal',
        'CPILFESL': 'navy'
    }
    
    # Normalize each series (0-100 scale)
    def normalize_series(series):
        series = series.dropna()
        if len(series) == 0 or series.max() == series.min():
            return series
        return (100 * (series - series.min()) / (series.max() - series.min())).tolist()
    
    # Add traces for each available indicator
    for indicator_id, df in data_dict.items():
        if df is not None:
            # Convert NaN to None for JSON serialization
            y_data = normalize_series(df[indicator_id])
            y_data = [None if pd.isna(y) else y for y in y_data]
            
            fig.add_trace(
                go.Scatter(
                    x=df.index.strftime('%Y-%m-%d').tolist(),
                    y=y_data,
                    name=FredData.INDICATORS.get(indicator_id, indicator_id),
                    line=dict(color=colors.get(indicator_id, 'black'))
                ),
                secondary_y=False
            )
    
    # Update layout
    fig.update_layout(
        title="Combined Economic Indicators (Normalized)",
        title_x=0.5,
        template='plotly_white',
        hovermode='x unified',
        height=500,
        margin=dict(l=40, r=20, t=60, b=80),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.5)'
        )
    )
    
    # Update axes labels
    fig.update_yaxes(
        title_text="Normalized Scale (0-100)",
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(211,211,211,0.5)',
        secondary_y=False
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