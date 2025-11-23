"""
Real-Time GPS Dashboard
Displays live GPS data from CSV files using Plotly Dash
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_leaflet as dl
import plotly.graph_objs as go
import pandas as pd
import os
from datetime import datetime
import glob
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__)

# Store for overlay toggles
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
    
    # Control Panel - top left (overlay filters)
    html.Div([
        html.Div("MAP OVERLAYS", style={
            'color': '#00ff9d',
            'fontSize': '10px',
            'fontWeight': '700',
            'letterSpacing': '2px',
            'marginBottom': '12px',
            'fontFamily': 'monospace'
        }),
        
        # Show Path Toggle
        html.Div([
            dcc.Checklist(
                id='show-path',
                options=[{'label': ' Path Trail', 'value': 'path'}],
                value=['path'],
                style={'color': '#fff', 'fontSize': '13px'}
            )
        ], style={'marginBottom': '8px'}),
        
        # Show Speed Graph Toggle
        html.Div([
            dcc.Checklist(
                id='show-speed-graph',
                options=[{'label': ' Speed Graph', 'value': 'speed'}],
                value=[],
                style={'color': '#fff', 'fontSize': '13px'}
            )
        ], style={'marginBottom': '8px'}),
        
        # Show Heatmap Toggle
        html.Div([
            dcc.Checklist(
                id='show-heatmap',
                options=[{'label': ' Location Heatmap', 'value': 'heatmap'}],
                value=[],
                style={'color': '#fff', 'fontSize': '13px'}
            )
        ], style={'marginBottom': '8px'}),
        
        # Show Statistics Toggle
        html.Div([
            dcc.Checklist(
                id='show-trip-stats',
                options=[{'label': ' Trip Statistics', 'value': 'stats'}],
                value=[],
                style={'color': '#fff', 'fontSize': '13px'}
            )
        ])
        
    ], style={
        'position': 'fixed',
        'top': '20px',
        'left': '20px',
        'backgroundColor': 'rgba(0, 0, 0, 0.85)',
        'padding': '16px 20px',
        'borderRadius': '8px',
        'border': '1px solid rgba(0, 255, 157, 0.3)',
        'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.6)',
        'backdropFilter': 'blur(10px)',
        'zIndex': 1001,
        'minWidth': '180px'
    }),
    
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
    
    # Speed Graph - bottom center (conditionally shown)
    html.Div(id='speed-graph-container', children=[
        dcc.Graph(
            id='speed-graph',
            config={'displayModeBar': False},
            style={'height': '200px', 'width': '500px'}
        )
    ], style={
        'position': 'fixed',
        'bottom': '20px',
        'left': '50%',
        'transform': 'translateX(-50%)',
        'backgroundColor': 'rgba(0, 0, 0, 0.85)',
        'padding': '12px',
        'borderRadius': '8px',
        'border': '1px solid rgba(0, 255, 157, 0.3)',
        'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.6)',
        'backdropFilter': 'blur(10px)',
        'zIndex': 1000,
        'display': 'none'  # Hidden by default
    }),
    
    # Trip Statistics - bottom right (conditionally shown)
    html.Div(id='trip-stats-panel', style={
        'position': 'fixed',
        'bottom': '20px',
        'right': '20px',
        'backgroundColor': 'rgba(0, 0, 0, 0.85)',
        'padding': '16px 20px',
        'borderRadius': '8px',
        'border': '1px solid rgba(0, 255, 157, 0.3)',
        'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.6)',
        'backdropFilter': 'blur(10px)',
        'zIndex': 1000,
        'minWidth': '200px',
        'display': 'none'  # Hidden by default
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


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula (in meters)"""
    R = 6371000  # Earth's radius in meters
    
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    delta_lat = np.radians(lat2 - lat1)
    delta_lon = np.radians(lon2 - lon1)
    
    a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c


@app.callback(
    [Output('gps-map', 'center'),
     Output('layer-group', 'children'),
     Output('stats-panel', 'children'),
     Output('last-update', 'children'),
     Output('speed-graph-container', 'style'),
     Output('speed-graph', 'figure'),
     Output('trip-stats-panel', 'style'),
     Output('trip-stats-panel', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('show-path', 'value'),
     Input('show-speed-graph', 'value'),
     Input('show-heatmap', 'value'),
     Input('show-trip-stats', 'value')]
)
def update_dashboard(n, show_path, show_speed_graph, show_heatmap, show_trip_stats):
    """Update all dashboard components with latest GPS data"""
    
    # Load data
    df, first_point = load_gps_data()
    
    # Default styles for conditional panels
    speed_graph_style = {
        'position': 'fixed',
        'bottom': '20px',
        'left': '50%',
        'transform': 'translateX(-50%)',
        'backgroundColor': 'rgba(0, 0, 0, 0.85)',
        'padding': '12px',
        'borderRadius': '8px',
        'border': '1px solid rgba(0, 255, 157, 0.3)',
        'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.6)',
        'backdropFilter': 'blur(10px)',
        'zIndex': 1000,
        'display': 'block' if 'speed' in show_speed_graph else 'none'
    }
    
    trip_stats_style = {
        'position': 'fixed',
        'bottom': '20px',
        'right': '20px',
        'backgroundColor': 'rgba(0, 0, 0, 0.85)',
        'padding': '16px 20px',
        'borderRadius': '8px',
        'border': '1px solid rgba(0, 255, 157, 0.3)',
        'boxShadow': '0 4px 16px rgba(0, 0, 0, 0.6)',
        'backdropFilter': 'blur(10px)',
        'zIndex': 1000,
        'minWidth': '200px',
        'display': 'block' if 'stats' in show_trip_stats else 'none'
    }
    
    if df.empty:
        empty_figure = go.Figure()
        empty_figure.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        return (
            [43.0731, -89.4012],
            [],
            html.Div("No data", style={'color': '#666', 'fontSize': '13px'}),
            "Waiting...",
            speed_graph_style,
            empty_figure,
            trip_stats_style,
            html.Div()
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
    
    # Calculate total distance
    total_distance = 0
    if len(df) > 1:
        for i in range(1, len(df)):
            dist = calculate_distance(
                df.iloc[i-1]['latitude'], df.iloc[i-1]['longitude'],
                df.iloc[i]['latitude'], df.iloc[i]['longitude']
            )
            total_distance += dist
    
    # Map center and layers
    map_center = [current_lat, current_lon]
    
    # Create path (polyline) from GPS points
    path_positions = [[row['latitude'], row['longitude']] for _, row in df.iterrows()]
    
    map_layers = []
    
    # Add path if enabled
    if 'path' in show_path:
        map_layers.append(
            dl.Polyline(
                positions=path_positions,
                color='#00ff9d',
                weight=4,
                opacity=0.9
            )
        )
    
    # Add heatmap if enabled
    if 'heatmap' in show_heatmap:
        # Create gradient heatmap based on speed - red (slow) to yellow (fast)
        heatmap_circles = []
        for idx, row in df.iterrows():
            # Calculate color based on speed (0-100 km/h range)
            speed_ratio = min(row['speed_kmh'] / 100, 1.0)
            
            # Gradient from purple (slow) -> orange (medium) -> red (fast)
            if speed_ratio < 0.5:
                # Purple to orange
                r = int(138 + (255 - 138) * (speed_ratio * 2))
                g = int(43 + (165 - 43) * (speed_ratio * 2))
                b = int(226 - 226 * (speed_ratio * 2))
            else:
                # Orange to red
                r = 255
                g = int(165 - 165 * ((speed_ratio - 0.5) * 2))
                b = 0
            
            color = f'rgb({r},{g},{b})'
            
            heatmap_circles.append(
                dl.CircleMarker(
                    center=[row['latitude'], row['longitude']],
                    radius=12,
                    color=color,
                    fillColor=color,
                    fillOpacity=0.3,
                    weight=1,
                    opacity=0.6
                )
            )
        map_layers.append(
            dl.LayerGroup(children=heatmap_circles, id='heatmap-layer')
        )
    
    # Add current position and markers
    map_layers.extend([
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
    ])
    
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
    
    # Create speed graph
    speed_figure = go.Figure()
    speed_figure.add_trace(go.Scatter(
        y=df['speed_kmh'],
        mode='lines',
        line=dict(color='#00ff9d', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 157, 0.1)',
        name='Speed'
    ))
    speed_figure.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.3)',
        font=dict(color='#00ff9d', family='monospace', size=10),
        margin=dict(l=40, r=20, t=30, b=30),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0, 255, 157, 0.1)',
            title='Data Points',
            title_font=dict(size=10)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0, 255, 157, 0.1)',
            title='Speed (km/h)',
            title_font=dict(size=10)
        ),
        title=dict(
            text='SPEED PROFILE',
            font=dict(size=12, color='#00ff9d'),
            x=0.5,
            xanchor='center'
        ),
        height=180
    )
    
    # Create trip statistics content
    trip_stats_content = html.Div([
        html.Div("TRIP STATS", style={
            'color': '#00ff9d',
            'fontSize': '11px',
            'fontWeight': '700',
            'letterSpacing': '2px',
            'marginBottom': '12px',
            'fontFamily': 'monospace'
        }),
        
        html.Div([
            html.Span("DIST  ", style={'color': '#555', 'fontSize': '10px', 'fontFamily': 'monospace'}),
            html.Span(f"{total_distance/1000:.2f} km", style={'color': '#fff', 'fontSize': '14px', 'fontFamily': 'monospace', 'fontWeight': '500'})
        ], style={'marginBottom': '8px'}),
        
        html.Div([
            html.Span("AVG   ", style={'color': '#555', 'fontSize': '10px', 'fontFamily': 'monospace'}),
            html.Span(f"{avg_speed:.1f} km/h", style={'color': '#fff', 'fontSize': '14px', 'fontFamily': 'monospace', 'fontWeight': '500'})
        ], style={'marginBottom': '8px'}),
        
        html.Div([
            html.Span("MAX   ", style={'color': '#555', 'fontSize': '10px', 'fontFamily': 'monospace'}),
            html.Span(f"{max_speed:.1f} km/h", style={'color': '#00ff9d', 'fontSize': '14px', 'fontFamily': 'monospace', 'fontWeight': '600'})
        ], style={'marginBottom': '8px'}),
        
        html.Div(style={'borderTop': '1px solid rgba(0, 255, 157, 0.2)', 'margin': '12px 0'}),
        
        html.Div([
            html.Span("ALT RANGE", style={'color': '#555', 'fontSize': '9px', 'fontFamily': 'monospace', 'display': 'block', 'marginBottom': '4px'}),
            html.Span(f"{min_alt:.0f} - {max_alt:.0f} m", style={'color': '#aaa', 'fontSize': '12px', 'fontFamily': 'monospace'})
        ], style={'marginBottom': '8px'}),
        
        html.Div([
            html.Span("POINTS", style={'color': '#555', 'fontSize': '9px', 'fontFamily': 'monospace', 'display': 'block', 'marginBottom': '4px'}),
            html.Span(f"{total_points:,}", style={'color': '#aaa', 'fontSize': '12px', 'fontFamily': 'monospace'})
        ])
    ])
    
    return (
        map_center,
        map_layers,
        stats_content,
        last_update,
        speed_graph_style,
        speed_figure,
        trip_stats_style,
        trip_stats_content
    )


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Starting Real-Time GPS Dashboard with Interactive Overlays")
    print("="*60)
    print("Dashboard: http://127.0.0.1:8050")
    print("Auto-refresh: Every 0.5 seconds")
    print("\nFeatures:")
    print("  • Toggle path trail on/off")
    print("  • Speed graph overlay")
    print("  • Location heatmap")
    print("  • Trip statistics panel")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=True, use_reloader=False)
