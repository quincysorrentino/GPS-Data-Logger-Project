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
            # Satellite imagery - Best for defense/tracking applications
            dl.TileLayer(url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
                        attribution='Tiles &copy; Esri'),
            dl.LayerGroup(id="layer-group")
        ],
        style={
            'width': '100%',
            'height': '100vh',
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'backgroundColor': '#1a1a1a'
        }
    ),
    
    # Stats display - bottom left
    html.Div(id='stats-panel', style={
        'position': 'fixed',
        'bottom': '20px',
        'left': '20px',
        'backgroundColor': 'rgba(26, 26, 26, 0.92)',
        'padding': '16px 20px',
        'borderRadius': '4px',
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.3)',
        'zIndex': 1000,
        'minWidth': '200px'
    }),
    
    # Update indicator - top right
    html.Div(id='last-update', style={
        'position': 'fixed',
        'top': '20px',
        'right': '20px',
        'backgroundColor': 'rgba(26, 26, 26, 0.92)',
        'padding': '8px 14px',
        'borderRadius': '4px',
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'boxShadow': '0 2px 8px rgba(0,0,0,0.3)',
        'zIndex': 1000,
        'fontSize': '11px',
        'color': '#888',
        'fontFamily': 'monospace'
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
        # Path trail
        dl.Polyline(
            positions=path_positions,
            color='#00d4ff',
            weight=3,
            opacity=0.8
        ),
        # Current position - Pulsing circle with direction indicator
        dl.CircleMarker(
            center=[current_lat, current_lon],
            radius=12,
            color='#00d4ff',
            fillColor='#0088ff',
            fillOpacity=0.3,
            weight=3,
            className='pulse',
            children=[
                dl.Tooltip(f"Speed: {current_speed:.1f} km/h | Course: {current_course:.0f}°"),
                dl.Popup([
                    html.Div([
                        html.H4("Active Target", style={'color': '#fff', 'margin': '0 0 10px 0'}),
                        html.P(f"Position: {current_lat:.6f}, {current_lon:.6f}", style={'color': '#ccc', 'margin': '5px 0'}),
                        html.P(f"Speed: {current_speed:.1f} km/h", style={'color': '#ccc', 'margin': '5px 0'}),
                        html.P(f"Heading: {current_course:.0f}°", style={'color': '#ccc', 'margin': '5px 0'}),
                        html.P(f"Altitude: {current_alt:.1f} m", style={'color': '#ccc', 'margin': '5px 0'}),
                        html.P(f"Satellites: {int(current_sats)}", style={'color': '#ccc', 'margin': '5px 0'}),
                        html.P(f"Signal: {'Good' if current_sats >= 8 else 'Weak'}", style={'color': '#00ff00' if current_sats >= 8 else '#ff9900', 'margin': '5px 0'})
                    ], style={'backgroundColor': '#1a1a1a', 'padding': '10px'})
                ])
            ]
        ),
        # Direction indicator - Small arrow showing heading
        dl.CircleMarker(
            center=[current_lat, current_lon],
            radius=4,
            color='#ffffff',
            fillColor='#ffffff',
            fillOpacity=1.0,
            weight=1
        ),
        # Start position - Small reference marker (use actual first point)
        dl.CircleMarker(
            center=[first_point['latitude'], first_point['longitude']] if first_point else [df.iloc[0]['latitude'], df.iloc[0]['longitude']],
            radius=5,
            color='#888888',
            fillColor='#444444',
            fillOpacity=0.5,
            weight=1,
            children=[
                dl.Tooltip("Origin Point")
            ]
        )
    ]
    
    # Dark mode minimal stats display
    stats_content = html.Div([
        # Large speed display
        html.Div([
            html.Span(f"{current_speed:.0f}", style={
                'fontSize': '48px',
                'fontWeight': '200',
                'color': '#00d4ff',
                'lineHeight': '1',
                'fontFamily': 'monospace'
            }),
            html.Span(" km/h", style={
                'fontSize': '14px',
                'color': '#666',
                'marginLeft': '6px',
                'verticalAlign': 'bottom'
            })
        ], style={'marginBottom': '16px'}),
        
        # Coordinates
        html.Div([
            html.Div([
                html.Span("LAT ", style={'color': '#666', 'fontSize': '11px', 'fontFamily': 'monospace'}),
                html.Span(f"{current_lat:.6f}", style={'color': '#aaa', 'fontSize': '13px', 'fontFamily': 'monospace'})
            ], style={'marginBottom': '4px'}),
            html.Div([
                html.Span("LON ", style={'color': '#666', 'fontSize': '11px', 'fontFamily': 'monospace'}),
                html.Span(f"{current_lon:.6f}", style={'color': '#aaa', 'fontSize': '13px', 'fontFamily': 'monospace'})
            ], style={'marginBottom': '12px'}),
        ]),
        
        # Other stats
        html.Div([
            html.Div([
                html.Span(f"{current_alt:.0f} ", style={'color': '#aaa', 'fontSize': '14px'}),
                html.Span("m", style={'color': '#666', 'fontSize': '12px'})
            ], style={'marginBottom': '6px'}),
            html.Div([
                html.Span(f"{current_course:.0f}°", style={'color': '#aaa', 'fontSize': '14px'})
            ], style={'marginBottom': '6px'}),
            html.Div([
                html.Span(f"{int(current_sats)} ", style={'color': '#aaa', 'fontSize': '14px'}),
                html.Span("sats", style={'color': '#666', 'fontSize': '12px'})
            ]),
        ], style={'borderTop': '1px solid rgba(255,255,255,0.1)', 'paddingTop': '12px', 'marginTop': '12px'})
    ])
    
    # Last update timestamp
    last_update = datetime.now().strftime('%H:%M:%S')
    
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
