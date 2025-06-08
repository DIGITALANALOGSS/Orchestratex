import logging
import json
from typing import Dict, Any, List
import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
from datetime import datetime
from ..core.project_manager import ProjectManager

class CompletionDashboard:
    def __init__(self, app: dash.Dash):
        """Initialize completion dashboard.
        
        Args:
            app: Dash application
        """
        self.logger = logging.getLogger(__name__)
        self.project_manager = ProjectManager()
        self.app = app
        self._setup_layout()
        self._setup_callbacks()
        
    def _setup_layout(self):
        """Setup dashboard layout."""
        self.app.layout = html.Div([
            # Header
            html.H1("Orchestratex Project Completion Dashboard"),
            
            # Project selector
            html.Div([
                html.Label("Select Project:"),
                dcc.Dropdown(
                    id='project-selector',
                    options=[],
                    value=None,
                    placeholder="Select a project..."
                )
            ]),
            
            # Progress overview
            html.Div([
                html.H2("Project Overview"),
                html.Div(id='project-overview'),
                dcc.Graph(id='progress-chart'),
                dcc.Graph(id='component-status')
            ]),
            
            # Component details
            html.Div([
                html.H2("Components"),
                html.Div(id='component-details'),
                html.Button('Refresh', id='refresh-btn', n_clicks=0)
            ]),
            
            # Interval refresh
            dcc.Interval(
                id='interval-component',
                interval=30 * 1000,  # 30 seconds
                n_intervals=0
            )
        ])
        
    def _setup_callbacks(self):
        """Setup dashboard callbacks."""
        @callback(
            Output('project-selector', 'options'),
            Input('interval-component', 'n_intervals'),
            Input('refresh-btn', 'n_clicks')
        )
        def update_project_selector(n, n_clicks):
            """Update project selector options."""
            projects = self.project_manager.list_projects()
            return [
                {'label': p['name'], 'value': p['id']}
                for p in projects
            ]
            
        @callback(
            Output('project-overview', 'children'),
            Output('progress-chart', 'figure'),
            Output('component-status', 'figure'),
            Output('component-details', 'children'),
            Input('project-selector', 'value'),
            Input('interval-component', 'n_intervals'),
            Input('refresh-btn', 'n_clicks')
        )
        def update_dashboard(project_id, n, n_clicks):
            """Update dashboard content."""
            if not project_id:
                return "", {}, {}, ""
                
            project = self.project_manager.get_project(project_id)
            if not project:
                return "Project not found", {}, {}, ""
                
            # Project overview
            overview = html.Div([
                html.P(f"Name: {project['name']}")
                html.P(f"Description: {project['description']}")
                html.P(f"Created: {project['created_at']}")
                html.P(f"Updated: {project['updated_at']}")
            ])
            
            # Progress chart
            progress = project['progress']
            progress_chart = go.Figure(
                data=[
                    go.Pie(
                        labels=['Completed', 'Remaining'],
                        values=[progress['completed'], progress['total'] - progress['completed']],
                        hole=.3
                    )
                ]
            )
            progress_chart.update_layout(
                title='Project Progress',
                showlegend=True
            )
            
            # Component status
            component_status = go.Figure(
                data=[
                    go.Bar(
                        x=list(project['components'].keys()),
                        y=[1 if c['status'] == 'complete' else 0 
                          for c in project['components'].values()],
                        name='Completed'
                    )
                ]
            )
            component_status.update_layout(
                title='Component Completion Status',
                yaxis_title='Completion Status'
            )
            
            # Component details
            component_details = html.Div([
                html.H3("Component Details"),
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th("Name"),
                            html.Th("Status"),
                            html.Th("Description")
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(c['name']),
                            html.Td(c['status']),
                            html.Td(c['description'])
                        ])
                        for c in project['components'].values()
                    ])
                ])
            ])
            
            return overview, progress_chart, component_status, component_details
            
    def run(self, host: str = '0.0.0.0', port: int = 8050):
        """Run the dashboard.
        
        Args:
            host: Host to run on
            port: Port to run on
        """
        self.app.run_server(host=host, port=port)
