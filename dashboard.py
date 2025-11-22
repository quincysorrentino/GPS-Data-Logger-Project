"""
Real-Time GPS Dashboard
Displays live GPS data from CSV files using Plotly Dash
"""

import dash
from dash import dcc, html, Input, Output
import dash_leaflet as dl
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime
import glob

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    # Fullscreen map with dark tiles
    dl.Map(
        id='gps-map',
        center=[43.0731, -89.4012],
        zoom=15,
        children=[
            # OpenStreetMap - Detailed with all buildings and streets labeled
            dl.TileLayer(url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                        attribution='© OpenStreetMap contributors'),
            dl.LayerGroup(id="layer-group")
        ],
        style={
            'width': '100%',
            'height': '100vh',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'backgroundColor': '#000000'
        }
    ),
    
    # Stats display - bottom left (sleek glassmorphism)
    html.Div(id='stats-panel', style={
        'position': 'fixed',
        'bottom': '20px',
        'left': '20px',
        'backgroundColor': 'rgba(0, 0, 0, 0.75)',
        'padding': '20px 24px',
        'borderRadius': '12px',
        'border': '1px solid rgba(0, 255, 157, 0.3)',
        'boxShadow': '0 8px 32px rgba(0, 0, 0, 0.6), 0 0 20px rgba(0, 255, 157, 0.1)',
        'backdropFilter': 'blur(10px)',
        'zIndex': 1000,
        'minWidth': '240px'
    }),
    
    # Update indicator - top right
    html.Div(id='last-update', style={
        'position': 'fixed',
        'top': '20px',
        'right': '20px',
        'backgroundColor': 'rgba(0, 0, 0, 0.75)',
        'padding': '10px 16px',
        'borderRadius': '8px',
        'border': '1px solid rgba(0, 255, 157, 0.3)',
        'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.6)',
        'backdropFilter': 'blur(10px)',
        'zIndex': 1000,
        'fontSize': '12px',
        'color': '#00ff9d',
        'fontFamily': 'monospace',
        'fontWeight': '500',
        'letterSpacing': '0.5px'
    }),
    
    # Interval component - update every 1 second for real-time feel
    dcc.Interval(
        id='interval-component',
        interval=0.5*1000,
        n_intervals=0
    )
], style={
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'margin': 0,
    'padding': 0,
    'height': '100vh',
    'overflow': 'hidden',
    'backgroundColor': '#1a1a1a'
})


def get_latest_csv():
    """Find the most recent GPS log CSV file"""
    csv_files = glob.glob('logs/gps_log_*.csv')
    if not csv_files:
        return None
    latest_file = max(csv_files, key=os.path.getctime)
    return latest_file


def load_gps_data():
    """Load GPS data from the latest CSV file"""
    csv_file = get_latest_csv()
    
    if not csv_file or not os.path.exists(csv_file):
        return pd.DataFrame(), None
    
    try:
        df = pd.read_csv(csv_file)
        
        # Filter out invalid data
        df = df[df['latitude'] != 0]
        df = df[df['longitude'] != 0]
        df = df[df['altitude'] != -999.0]
        
        # Store the actual first point
        first_point = None
        if len(df) > 0:
            first_point = {
                'latitude': df.iloc[0]['latitude'],
                'longitude': df.iloc[0]['longitude']
            }
        
        return df, first_point
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(), None


@app.callback(
    [Output('gps-map', 'center'),
     Output('layer-group', 'children'),
     Output('stats-panel', 'children'),
     Output('last-update', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update all dashboard components with latest GPS data"""
    
    # Load data
    df, first_point = load_gps_data()
    
    if df.empty:
        return (
            [43.0731, -89.4012],
            [],
            html.Div("No data", style={'color': '#666', 'fontSize': '13px'}),
            "Waiting..."
        )
    
    # Get current (latest) position
    current_lat = df.iloc[-1]['latitude']
    current_lon = df.iloc[-1]['longitude']
    current_speed = df.iloc[-1]['speed_kmh']
    current_alt = df.iloc[-1]['altitude']
    current_sats = df.iloc[-1]['satellites']
    current_course = df.iloc[-1]['course']
    
    # Calculate statistics
    total_points = len(df)
    avg_speed = df['speed_kmh'].mean()
    max_speed = df['speed_kmh'].max()
    min_alt = df['altitude'].min()
    max_alt = df['altitude'].max()
    
    # Map center and layers
    map_center = [current_lat, current_lon]
    
    # Create path (polyline) from GPS points
    path_positions = [[row['latitude'], row['longitude']] for _, row in df.iterrows()]
    
    map_layers = [
        # Path trail - Neon green glow
        dl.Polyline(
            positions=path_positions,
            color='#00ff9d',
            weight=4,
            opacity=0.9
        ),
        # Current position - Pulsing neon circle
        dl.CircleMarker(
            center=[current_lat, current_lon],
            radius=14,
            color='#00ff9d',
            fillColor='#00ff9d',
            fillOpacity=0.4,
            weight=3,
            className='pulse',
            children=[
                dl.Tooltip(f"Speed: {current_speed:.1f} km/h | Course: {current_course:.0f}°"),
                dl.Popup([
                    html.Div([
                        html.H4("◉ ACTIVE SIGNAL", style={'color': '#00ff9d', 'margin': '0 0 12px 0', 'fontSize': '14px', 'letterSpacing': '2px', 'fontWeight': '700'}),
                        html.P(f"LAT  {current_lat:.6f}", style={'color': '#fff', 'margin': '6px 0', 'fontFamily': 'monospace', 'fontSize': '12px'}),
                        html.P(f"LON  {current_lon:.6f}", style={'color': '#fff', 'margin': '6px 0', 'fontFamily': 'monospace', 'fontSize': '12px'}),
                        html.Div(style={'borderTop': '1px solid rgba(0, 255, 157, 0.3)', 'margin': '10px 0'}),
                        html.P(f"SPEED    {current_speed:.1f} km/h", style={'color': '#aaa', 'margin': '5px 0', 'fontFamily': 'monospace', 'fontSize': '11px'}),
                        html.P(f"HEADING  {current_course:.0f}°", style={'color': '#aaa', 'margin': '5px 0', 'fontFamily': 'monospace', 'fontSize': '11px'}),
                        html.P(f"ALT      {current_alt:.1f} m", style={'color': '#aaa', 'margin': '5px 0', 'fontFamily': 'monospace', 'fontSize': '11px'}),
                        html.P(f"SATS     {int(current_sats)}", style={'color': '#00ff9d' if current_sats >= 8 else '#ff6b00', 'margin': '5px 0', 'fontFamily': 'monospace', 'fontSize': '11px', 'fontWeight': '600'})
                    ], style={'backgroundColor': '#000', 'padding': '14px', 'border': '1px solid rgba(0, 255, 157, 0.3)'})
                ])
            ]
        ),
        # Direction indicator - Bright center dot
        dl.CircleMarker(
            center=[current_lat, current_lon],
            radius=5,
            color='#ffffff',
            fillColor='#ffffff',
            fillOpacity=1.0,
            weight=2
        ),
        # Start position - Dimmed marker
        dl.CircleMarker(
            center=[first_point['latitude'], first_point['longitude']] if first_point else [df.iloc[0]['latitude'], df.iloc[0]['longitude']],
            radius=6,
            color='#555555',
            fillColor='#222222',
            fillOpacity=0.6,
            weight=2,
            children=[
                dl.Tooltip("ORIGIN")
            ]
        )
    ]
    
    # Sleek cyberpunk stats display
    stats_content = html.Div([
        # Large speed display with neon glow
        html.Div([
            html.Span(f"{current_speed:.0f}", style={
                'fontSize': '64px',
                'fontWeight': '200',
                'color': '#00ff9d',
                'lineHeight': '1',
                'fontFamily': 'monospace',
                'textShadow': '0 0 20px rgba(0, 255, 157, 0.6)'
            }),
            html.Span(" km/h", style={
                'fontSize': '16px',
                'color': '#666',
                'marginLeft': '8px',
                'verticalAlign': 'bottom',
                'letterSpacing': '1px'
            })
        ], style={'marginBottom': '20px'}),
        
        # Coordinates with monospace styling
        html.Div([
            html.Div([
                html.Span("LAT  ", style={'color': '#555', 'fontSize': '10px', 'fontFamily': 'monospace', 'letterSpacing': '2px'}),
                html.Span(f"{current_lat:.6f}", style={'color': '#00ff9d', 'fontSize': '14px', 'fontFamily': 'monospace', 'fontWeight': '500'})
            ], style={'marginBottom': '6px'}),
            html.Div([
                html.Span("LON  ", style={'color': '#555', 'fontSize': '10px', 'fontFamily': 'monospace', 'letterSpacing': '2px'}),
                html.Span(f"{current_lon:.6f}", style={'color': '#00ff9d', 'fontSize': '14px', 'fontFamily': 'monospace', 'fontWeight': '500'})
            ], style={'marginBottom': '16px'}),
        ]),
        
        # Neon separator
        html.Div(style={'borderTop': '1px solid rgba(0, 255, 157, 0.2)', 'margin': '16px 0', 'boxShadow': '0 0 10px rgba(0, 255, 157, 0.1)'}),
        
        # Other stats in grid
        html.Div([
            html.Div([
                html.Span("ALT  ", style={'color': '#555', 'fontSize': '10px', 'fontFamily': 'monospace', 'letterSpacing': '2px'}),
                html.Span(f"{current_alt:.0f} m", style={'color': '#fff', 'fontSize': '16px', 'fontFamily': 'monospace', 'fontWeight': '300'})
            ], style={'marginBottom': '8px'}),
            html.Div([
                html.Span("HDG  ", style={'color': '#555', 'fontSize': '10px', 'fontFamily': 'monospace', 'letterSpacing': '2px'}),
                html.Span(f"{current_course:.0f}°", style={'color': '#fff', 'fontSize': '16px', 'fontFamily': 'monospace', 'fontWeight': '300'})
            ], style={'marginBottom': '8px'}),
            html.Div([
                html.Span("SAT  ", style={'color': '#555', 'fontSize': '10px', 'fontFamily': 'monospace', 'letterSpacing': '2px'}),
                html.Span(f"{int(current_sats)}", style={'color': '#00ff9d' if current_sats >= 8 else '#ff6b00', 'fontSize': '16px', 'fontFamily': 'monospace', 'fontWeight': '500'}),
                html.Span(f"  {'●' * min(int(current_sats), 12)}", style={'color': '#00ff9d' if current_sats >= 8 else '#ff6b00', 'fontSize': '8px', 'marginLeft': '6px'})
            ]),
        ], style={'marginTop': '12px'})
    ])
    
    # Last update timestamp with live indicator
    last_update = f"● LIVE  {datetime.now().strftime('%H:%M:%S')}"
    
    return (
        map_center,
        map_layers,
        stats_content,
        last_update
    )


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Real-Time GPS Dashboard")
    print("="*60)
    print("Dashboard: http://127.0.0.1:8050")
    print("Auto-refresh: Every 2 seconds")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=True, use_reloader=False)
