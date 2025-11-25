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
    # Header
    html.Div([
        html.H1("GPS TELEMETRY", style={
            'fontSize': '18px',
            'fontWeight': '600',
            'letterSpacing': '0.5px',
            'margin': '0',
            'background': 'linear-gradient(90deg, #4facfe 0%, #00f2fe 100%)',
            'WebkitBackgroundClip': 'text',
            'WebkitTextFillColor': 'transparent',
            'backgroundClip': 'text',
            'color': 'transparent'
        }),
        html.Div([
            html.Div(style={
                'width': '8px',
                'height': '8px',
                'borderRadius': '50%',
                'backgroundColor': '#00ff88',
                'boxShadow': '0 0 10px #00ff88'
            }),
            html.Span(id='last-update', children="Waiting for signal...")
        ], style={
            'display': 'flex',
            'alignItems': 'center',
            'gap': '8px',
            'fontSize': '12px',
            'color': '#a0a0a0'
        })
    ], style={
        'position': 'fixed',
        'top': '20px',
        'left': '50%',
        'transform': 'translateX(-50%)',
        'padding': '12px 30px',
        'zIndex': 1002,
        'display': 'flex',
        'alignItems': 'center',
        'gap': '15px',
        'background': 'rgba(20, 20, 30, 0.75)',
        'backdropFilter': 'blur(12px)',
        'WebkitBackdropFilter': 'blur(12px)',
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'borderRadius': '16px',
        'boxShadow': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'color': '#ffffff'
    }),

    # Fullscreen map with dark tiles
    dl.Map(
        id='gps-map',
        center=[43.0731, -89.4012],
        zoom=15,
        children=[
            dl.LayersControl(
                [
                    dl.BaseLayer(
                        dl.TileLayer(
                            url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                        ),
                        name="Dark Matter",
                        checked=True
                    ),
                    dl.BaseLayer(
                        dl.TileLayer(
                            url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                            attribution='&copy; OpenStreetMap contributors'
                        ),
                        name="OpenStreetMap"
                    ),
                    dl.BaseLayer(
                        dl.TileLayer(
                            url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                            attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
                        ),
                        name="Satellite"
                    ),
                ] + 
                [
                    dl.Overlay(dl.LayerGroup(id="layer-group"), name="Data Layers", checked=True)
                ]
            )
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
    
    # Control Panel - top left (overlay filters)
    html.Div([
        html.Div("Map Overlays", style={
            'color': '#4facfe',
            'fontSize': '14px',
            'fontWeight': '600',
            'textTransform': 'uppercase',
            'letterSpacing': '1px',
            'marginBottom': '15px',
            'borderBottom': '1px solid rgba(255, 255, 255, 0.1)',
            'paddingBottom': '8px'
        }),
        
        # Show Path Toggle
        html.Div([
            dcc.Checklist(
                id='show-path',
                options=[{'label': ' Path Trail', 'value': 'path'}],
                value=['path'],
                style={'color': '#cccccc', 'fontSize': '14px'},
                inputStyle={"margin-right": "10px", "cursor": "pointer"}
            )
        ], style={'marginBottom': '10px'}),
        
        # Show Speed Graph Toggle
        html.Div([
            dcc.Checklist(
                id='show-speed-graph',
                options=[{'label': ' Speed Graph', 'value': 'speed'}],
                value=[],
                style={'color': '#cccccc', 'fontSize': '14px'},
                inputStyle={"margin-right": "10px", "cursor": "pointer"}
            )
        ], style={'marginBottom': '10px'}),
        
        # Show Heatmap Toggle
        html.Div([
            dcc.Checklist(
                id='show-heatmap',
                options=[{'label': ' Location Heatmap', 'value': 'heatmap'}],
                value=[],
                style={'color': '#cccccc', 'fontSize': '14px'},
                inputStyle={"margin-right": "10px", "cursor": "pointer"}
            )
        ], style={'marginBottom': '10px'}),
        
        # Show Statistics Toggle
        html.Div([
            dcc.Checklist(
                id='show-trip-stats',
                options=[{'label': ' Trip Statistics', 'value': 'stats'}],
                value=['stats'],
                style={'color': '#cccccc', 'fontSize': '14px'},
                inputStyle={"margin-right": "10px", "cursor": "pointer"}
            )
        ])
        
    ], style={
        'position': 'fixed',
        'top': '20px',
        'left': '20px',
        'padding': '20px',
        'zIndex': 1001,
        'minWidth': '220px',
        'background': 'rgba(20, 20, 30, 0.75)',
        'backdropFilter': 'blur(12px)',
        'WebkitBackdropFilter': 'blur(12px)',
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'borderRadius': '16px',
        'boxShadow': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'color': '#ffffff'
    }),
    
    # Stats display - bottom left (professional panel)
    html.Div(id='stats-panel', style={
        'position': 'fixed',
        'bottom': '20px',
        'left': '20px',
        'padding': '24px',
        'zIndex': 1000,
        'minWidth': '280px',
        'display': 'grid',
        'gridTemplateColumns': '1fr 1fr',
        'gap': '15px',
        'background': 'rgba(20, 20, 30, 0.75)',
        'backdropFilter': 'blur(12px)',
        'WebkitBackdropFilter': 'blur(12px)',
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'borderRadius': '16px',
        'boxShadow': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'color': '#ffffff'
    }),
    
    # Speed Graph - bottom center (conditionally shown)
    html.Div(id='speed-graph-container', children=[
        dcc.Graph(
            id='speed-graph',
            config={'displayModeBar': False},
            style={'height': '180px', 'width': '500px'}
        )
    ], style={'display': 'none'}),
    
    # Trip Statistics - bottom right (conditionally shown)
    html.Div(id='trip-stats-panel', style={'display': 'none'}),
    
    # Interval component - update every 1 second for real-time feel
    dcc.Interval(
        id='interval-component',
        interval=1000, # 1 second
        n_intervals=0
    )
], style={
    'fontFamily': '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'margin': 0,
    'padding': 0,
    'height': '100vh',
    'overflow': 'hidden',
    'backgroundColor': '#1a1a1a',
    'color': '#e0e0e0'
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
    glass_panel_style = {
        'background': 'rgba(20, 20, 30, 0.75)',
        'backdropFilter': 'blur(12px)',
        'WebkitBackdropFilter': 'blur(12px)',
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'borderRadius': '16px',
        'boxShadow': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'color': '#ffffff',
        'zIndex': 1000
    }

    speed_graph_style = {
        **glass_panel_style,
        'position': 'fixed',
        'bottom': '20px',
        'left': '50%',
        'transform': 'translateX(-50%)',
        'padding': '15px',
        'display': 'block' if 'speed' in show_speed_graph else 'none'
    }
    
    trip_stats_style = {
        **glass_panel_style,
        'position': 'fixed',
        'bottom': '20px',
        'right': '20px',
        'padding': '20px',
        'minWidth': '220px',
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
                color='#2563eb',
                weight=4,
                opacity=0.8
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
        # Current position - Active marker
        dl.CircleMarker(
            center=[current_lat, current_lon],
            radius=14,
            color='#2563eb',
            fillColor='#2563eb',
            fillOpacity=0.3,
            weight=3,
            className='pulse',
            children=[
                dl.Tooltip(f"Speed: {current_speed:.1f} km/h | Course: {current_course:.0f}°"),
                dl.Popup([
                    html.Div([
                        html.H4("Current Position", style={'color': '#1e40af', 'margin': '0 0 12px 0', 'fontSize': '14px', 'fontWeight': '600'}),
                        html.P(f"Latitude: {current_lat:.6f}", style={'color': '#333', 'margin': '6px 0', 'fontSize': '12px'}),
                        html.P(f"Longitude: {current_lon:.6f}", style={'color': '#333', 'margin': '6px 0', 'fontSize': '12px'}),
                        html.Div(style={'borderTop': '1px solid #e5e7eb', 'margin': '10px 0'}),
                        html.P(f"Speed: {current_speed:.1f} km/h", style={'color': '#666', 'margin': '5px 0', 'fontSize': '11px'}),
                        html.P(f"Heading: {current_course:.0f}°", style={'color': '#666', 'margin': '5px 0', 'fontSize': '11px'}),
                        html.P(f"Altitude: {current_alt:.1f} m", style={'color': '#666', 'margin': '5px 0', 'fontSize': '11px'}),
                        html.P(f"Satellites: {int(current_sats)}", style={'color': '#2563eb' if current_sats >= 8 else '#dc2626', 'margin': '5px 0', 'fontSize': '11px', 'fontWeight': '600'})
                    ], style={'backgroundColor': '#fff', 'padding': '14px', 'border': '1px solid #e5e7eb'})
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
        # Start position - Origin marker
        dl.CircleMarker(
            center=[first_point['latitude'], first_point['longitude']] if first_point else [df.iloc[0]['latitude'], df.iloc[0]['longitude']],
            radius=6,
            color='#64748b',
            fillColor='#94a3b8',
            fillOpacity=0.6,
            weight=2,
            children=[
                dl.Tooltip("Start")
            ]
        )
    ])
    
    # Professional stats display
    stats_content = html.Div([
        # Large speed display
        html.Div([
            html.Span(f"{current_speed:.0f}", style={
                'fontSize': '56px',
                'fontWeight': '300',
                'color': '#4facfe',
                'lineHeight': '1'
            }),
            html.Span(" km/h", style={
                'fontSize': '16px',
                'color': '#a0a0a0',
                'marginLeft': '8px',
                'verticalAlign': 'bottom'
            })
        ], style={'marginBottom': '20px'}),
        
        # Coordinates
        html.Div([
            html.Div([
                html.Span("Latitude: ", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
                html.Span(f"{current_lat:.6f}", style={'color': '#fff', 'fontSize': '13px', 'fontWeight': '500', 'marginLeft': '8px'})
            ], style={'marginBottom': '6px', 'display': 'flex', 'justifyContent': 'space-between'}),
            html.Div([
                html.Span("Longitude: ", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '0.5px'}),
                html.Span(f"{current_lon:.6f}", style={'color': '#fff', 'fontSize': '13px', 'fontWeight': '500', 'marginLeft': '8px'})
            ], style={'marginBottom': '16px', 'display': 'flex', 'justifyContent': 'space-between'}),
        ]),
        
        # Separator
        html.Div(style={'borderTop': '1px solid rgba(255, 255, 255, 0.1)', 'margin': '16px 0'}),
        
        # Other stats
        html.Div([
            html.Div([
                html.Span("Altitude", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase'}),
                html.Span(f"{current_alt:.0f} m", style={'color': '#fff', 'fontSize': '14px', 'fontWeight': '500'})
            ], style={'marginBottom': '8px', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
            html.Div([
                html.Span("Heading", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase'}),
                html.Span(f"{current_course:.0f}°", style={'color': '#fff', 'fontSize': '14px', 'fontWeight': '500'})
            ], style={'marginBottom': '8px', 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
            html.Div([
                html.Span("Satellites", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase'}),
                html.Span(f"{int(current_sats)}", style={'color': '#4facfe' if current_sats >= 8 else '#ff5555', 'fontSize': '14px', 'fontWeight': '600'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}),
        ], style={'marginTop': '12px'})
    ])
    
    # Last update timestamp with live indicator
    last_update = f"Live • {datetime.now().strftime('%H:%M:%S')}"
    
    # Create speed graph
    speed_figure = go.Figure()
    speed_figure.add_trace(go.Scatter(
        y=df['speed_kmh'],
        mode='lines',
        line=dict(color='#4facfe', width=2),
        fill='tozeroy',
        fillcolor='rgba(79, 172, 254, 0.1)',
        name='Speed'
    ))
    speed_figure.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ccc', family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=10),
        margin=dict(l=40, r=20, t=30, b=30),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            title='Data Points',
            title_font=dict(size=10, color='#888')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            title='Speed (km/h)',
            title_font=dict(size=10, color='#888')
        ),
        title=dict(
            text='Speed Profile',
            font=dict(size=12, color='#4facfe'),
            x=0.5,
            xanchor='center'
        ),
        height=180
    )
    
    # Create trip statistics content
    trip_stats_content = html.Div([
        html.Div("Trip Statistics", style={
            'color': '#4facfe',
            'fontSize': '14px',
            'fontWeight': '600',
            'textTransform': 'uppercase',
            'letterSpacing': '1px',
            'marginBottom': '15px',
            'borderBottom': '1px solid rgba(255, 255, 255, 0.1)',
            'paddingBottom': '8px'
        }),
        
        html.Div([
            html.Span("Distance", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase'}),
            html.Span(f"{total_distance/1000:.2f} km", style={'color': '#fff', 'fontSize': '13px', 'fontWeight': '500'})
        ], style={'marginBottom': '8px', 'display': 'flex', 'justifyContent': 'space-between'}),
        
        html.Div([
            html.Span("Avg Speed", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase'}),
            html.Span(f"{avg_speed:.1f} km/h", style={'color': '#fff', 'fontSize': '13px', 'fontWeight': '500'})
        ], style={'marginBottom': '8px', 'display': 'flex', 'justifyContent': 'space-between'}),
        
        html.Div([
            html.Span("Max Speed", style={'color': '#888', 'fontSize': '11px', 'textTransform': 'uppercase'}),
            html.Span(f"{max_speed:.1f} km/h", style={'color': '#4facfe', 'fontSize': '13px', 'fontWeight': '600'})
        ], style={'marginBottom': '8px', 'display': 'flex', 'justifyContent': 'space-between'}),
        
        html.Div(style={'borderTop': '1px solid rgba(255, 255, 255, 0.1)', 'margin': '12px 0'}),
        
        html.Div([
            html.Span("Altitude Range", style={'color': '#888', 'fontSize': '10px', 'display': 'block', 'marginBottom': '4px', 'textTransform': 'uppercase'}),
            html.Span(f"{min_alt:.0f} - {max_alt:.0f} m", style={'color': '#ccc', 'fontSize': '12px'})
        ], style={'marginBottom': '8px'}),
        
        html.Div([
            html.Span("Data Points", style={'color': '#888', 'fontSize': '10px', 'display': 'block', 'marginBottom': '4px', 'textTransform': 'uppercase'}),
            html.Span(f"{total_points:,}", style={'color': '#ccc', 'fontSize': '12px'})
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
