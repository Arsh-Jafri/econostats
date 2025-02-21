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

def create_dashboard_components(cpi_df, savings_df, consumption_df):
    """
    Create all visualization components for the dashboard
    """
    plots_data = {}
    tables_html = {}
    
    # Create the plots and tables only for available data
    if cpi_df is not None:
        cpi_plot = create_time_series_plot(
            cpi_df, 
            'Consumer Price Index (CPI)', 
            'CPI'
        )
        plots_data['cpi'] = cpi_plot.to_dict()  # Convert to dict instead of HTML
        tables_html['cpi'] = create_summary_table(cpi_df)
    
    if savings_df is not None:
        savings_plot = create_time_series_plot(
            savings_df, 
            'Personal Savings Rate', 
            'Savings Rate (%)'
        )
        plots_data['savings'] = savings_plot.to_dict()  # Convert to dict instead of HTML
        tables_html['savings'] = create_summary_table(savings_df)
    
    if consumption_df is not None:
        consumption_plot = create_time_series_plot(
            consumption_df, 
            'Personal Consumption Expenditures', 
            'Expenditures (Billions $)'
        )
        plots_data['consumption'] = consumption_plot.to_dict()  # Convert to dict instead of HTML
        tables_html['consumption'] = create_summary_table(consumption_df)
    
    return plots_data, tables_html

def create_combined_plot(cpi_df, savings_df, consumption_df):
    """
    Create a combined plot with all indicators (normalized)
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Normalize each series (0-100 scale)
    def normalize_series(series):
        series = series.dropna()
        if len(series) == 0 or series.max() == series.min():
            return series
        return (100 * (series - series.min()) / (series.max() - series.min())).tolist()
    
    # Add traces only for available data
    if cpi_df is not None:
        fig.add_trace(
            go.Scatter(
                x=cpi_df.index.strftime('%Y-%m-%d').tolist(),
                y=normalize_series(cpi_df['CPIAUCSL']),
                name="CPI",
                line=dict(color='blue')
            ),
            secondary_y=False
        )
    
    if savings_df is not None:
        fig.add_trace(
            go.Scatter(
                x=savings_df.index.strftime('%Y-%m-%d').tolist(),
                y=normalize_series(savings_df['PSAVERT']),
                name="Savings Rate",
                line=dict(color='green')
            ),
            secondary_y=False
        )
    
    if consumption_df is not None:
        fig.add_trace(
            go.Scatter(
                x=consumption_df.index.strftime('%Y-%m-%d').tolist(),
                y=normalize_series(consumption_df['PCEC']),
                name="Consumption",
                line=dict(color='red')
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
        margin=dict(l=40, r=20, t=60, b=80),  # Adjusted margins
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=-0.2,  # Position below the plot
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