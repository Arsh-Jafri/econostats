import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_time_series_plot(df, title, y_label):
    """
    Create an interactive time series plot using Plotly
    """
    # Get the column name from the dataframe
    value_col = df.columns[0]
    
    fig = px.line(df, 
                  x=df.index,
                  y=value_col,
                  title=title,
                  labels={value_col: y_label},
                  template='plotly_white')
    
    # Customize the layout
    fig.update_layout(
        hovermode='x unified',
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        title_font_size=20,
        showlegend=True,
        legend_title_text='Indicators',
        height=400,  # Set a fixed height
        margin=dict(l=50, r=50, t=80, b=50)  # Add margins
    )
    
    # Enhance the hover information using correct Plotly syntax
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

def create_dashboard_components(cpi_df, savings_df, consumption_df):
    """
    Create all visualization components for the dashboard
    """
    # Create the plots
    cpi_plot = create_time_series_plot(
        cpi_df, 
        'Consumer Price Index (CPI)', 
        'CPI'
    )
    
    savings_plot = create_time_series_plot(
        savings_df, 
        'Personal Savings Rate', 
        'Savings Rate (%)'
    )
    
    consumption_plot = create_time_series_plot(
        consumption_df, 
        'Personal Consumption Expenditures', 
        'Expenditures (Billions $)'
    )
    
    # Create summary tables
    cpi_table = create_summary_table(cpi_df)
    savings_table = create_summary_table(savings_df)
    consumption_table = create_summary_table(consumption_df)
    
    # Convert plots to HTML
    plots_html = {
        'cpi': cpi_plot.to_html(full_html=False, include_plotlyjs=False),
        'savings': savings_plot.to_html(full_html=False, include_plotlyjs=False),
        'consumption': consumption_plot.to_html(full_html=False, include_plotlyjs=False)
    }
    
    tables_html = {
        'cpi': cpi_table,
        'savings': savings_table,
        'consumption': consumption_table
    }
    
    return plots_html, tables_html

def create_combined_plot(cpi_df, savings_df, consumption_df):
    """
    Create a combined plot with all indicators (normalized)
    """
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Normalize each series (0-100 scale)
    def normalize_series(series):
        series = series.dropna()
        if len(series) == 0 or series.max() == series.min():
            return series
        return 100 * (series - series.min()) / (series.max() - series.min())
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=cpi_df.index, y=normalize_series(cpi_df['CPIAUCSL']),
                  name="CPI", line=dict(color='blue')),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=savings_df.index, y=normalize_series(savings_df['PSAVERT']),
                  name="Savings Rate", line=dict(color='green')),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(x=consumption_df.index, y=normalize_series(consumption_df['PCEC']),
                  name="Consumption", line=dict(color='red')),
        secondary_y=False
    )
    
    # Update layout
    fig.update_layout(
        title="Combined Economic Indicators (Normalized)",
        title_x=0.5,
        template='plotly_white',
        hovermode='x unified',
        height=500,  # Taller plot for the combined view
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Update axes labels
    fig.update_yaxes(title_text="Normalized Scale (0-100)", secondary_y=False)
    
    return fig 

def filter_dataframe(df, start_date, end_date):
    """
    Filter a dataframe based on date range
    """
    if df is None:
        return None
    
    mask = (df.index >= start_date) & (df.index <= end_date)
    return df.loc[mask] 