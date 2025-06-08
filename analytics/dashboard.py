import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import logging
from monitoring.monitor import Monitor
from ml.model_manager import ModelManager

class AnalyticsDashboard:
    def __init__(self, update_interval: int = 5):
        """Initialize the analytics dashboard.
        
        Args:
            update_interval: Dashboard update interval in seconds
        """
        self.update_interval = update_interval
        self.logger = logging.getLogger(__name__)
        self.monitor = Monitor(interval=update_interval)
        self.model_manager = ModelManager()
        
        # Initialize Dash app
        self.app = dash.Dash(__name__)
        self._setup_layout()
        self._setup_callbacks()
        
    def _setup_layout(self):
        """Set up the dashboard layout."""
        self.app.layout = html.Div([
            html.H1("Orchestratex Analytics Dashboard"),
            
            # System Metrics
            html.Div([
                html.H2("System Performance"),
                dcc.Graph(id='cpu-metrics'),
                dcc.Graph(id='memory-metrics'),
                dcc.Graph(id='disk-metrics'),
                dcc.Graph(id='network-metrics')
            ]),
            
            # AI/ML Metrics
            html.Div([
                html.H2("AI/ML Performance"),
                dcc.Graph(id='model-performance'),
                dcc.Graph(id='prediction-trends'),
                dcc.Graph(id='error-rates')
            ]),
            
            # User Analytics
            html.Div([
                html.H2("User Analytics"),
                dcc.Graph(id='user-activity'),
                dcc.Graph(id='user-engagement'),
                dcc.Graph(id='usage-patterns')
            ]),
            
            # Update interval
            dcc.Interval(
                id='interval-component',
                interval=self.update_interval * 1000,  # in milliseconds
                n_intervals=0
            )
        ])
        
    def _setup_callbacks(self):
        """Set up callback functions."""
        @self.app.callback(
            [dash.dependencies.Output('cpu-metrics', 'figure'),
             dash.dependencies.Output('memory-metrics', 'figure'),
             dash.dependencies.Output('disk-metrics', 'figure'),
             dash.dependencies.Output('network-metrics', 'figure')],
            [dash.dependencies.Input('interval-component', 'n_intervals')]
        )
        def update_system_metrics(n):
            metrics = self.monitor.get_performance_metrics()
            
            # CPU Metrics
            cpu_fig = px.line(
                pd.DataFrame(metrics['cpu']),
                x='timestamp',
                y='cpu_percent',
                title='CPU Usage'
            )
            
            # Memory Metrics
            memory_fig = px.line(
                pd.DataFrame(metrics['memory']),
                x='timestamp',
                y=['memory_percent', 'memory_available'],
                title='Memory Usage'
            )
            
            # Disk Metrics
            disk_fig = px.line(
                pd.DataFrame(metrics['disk']),
                x='timestamp',
                y=['disk_percent', 'disk_free'],
                title='Disk Usage'
            )
            
            # Network Metrics
            network_fig = px.line(
                pd.DataFrame(metrics['network']),
                x='timestamp',
                y=['network_bytes_sent', 'network_bytes_recv'],
                title='Network Usage'
            )
            
            return cpu_fig, memory_fig, disk_fig, network_fig
            
        @self.app.callback(
            [dash.dependencies.Output('model-performance', 'figure'),
             dash.dependencies.Output('prediction-trends', 'figure'),
             dash.dependencies.Output('error-rates', 'figure')],
            [dash.dependencies.Input('interval-component', 'n_intervals')]
        )
        def update_ml_metrics(n):
            models = self.model_manager.list_models()
            
            # Model Performance
            performance_fig = px.bar(
                pd.DataFrame([
                    {
                        'model': model,
                        'accuracy': metadata.get('accuracy', 0),
                        'precision': metadata.get('precision', 0),
                        'recall': metadata.get('recall', 0)
                    }
                    for model, metadata in models.items()
                ]),
                x='model',
                y=['accuracy', 'precision', 'recall'],
                title='Model Performance'
            )
            
            # Prediction Trends
            trends_fig = px.line(
                pd.DataFrame([
                    {
                        'timestamp': metadata.get('timestamp', ''),
                        'accuracy': metadata.get('accuracy', 0)
                    }
                    for metadata in models.values()
                ]),
                x='timestamp',
                y='accuracy',
                title='Prediction Accuracy Trends'
            )
            
            # Error Rates
            error_fig = px.bar(
                pd.DataFrame([
                    {
                        'model': model,
                        'error_rate': 1 - metadata.get('accuracy', 0)
                    }
                    for model, metadata in models.items()
                ]),
                x='model',
                y='error_rate',
                title='Error Rates'
            )
            
            return performance_fig, trends_fig, error_fig
            
    def run(self, host: str = '0.0.0.0', port: int = 8050):
        """Run the dashboard server.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        try:
            self.monitor.start()
            self.app.run_server(
                host=host,
                port=port,
                debug=True
            )
        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {str(e)}")
            raise
            
    def stop(self):
        """Stop the dashboard."""
        self.monitor.stop()
