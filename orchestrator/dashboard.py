import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orchestratex.models.workflow import Workflow, WorkflowStage, WorkflowTask, AgentSession, AgentMetric
from orchestratex.database import get_db
import pandas as pd

# Initialize database connection
engine = create_engine(get_db())
Session = sessionmaker(bind=engine)

def get_workflow_metrics():
    """Get metrics for workflows."""
    db = Session()
    try:
        # Get workflow statistics
        workflows = db.query(Workflow).all()
        
        # Convert to DataFrame
        workflow_data = pd.DataFrame([
            {
                'name': w.name,
                'status': w.status,
                'created_at': w.created_at,
                'duration': (w.updated_at - w.created_at).total_seconds() if w.updated_at else None
            }
            for w in workflows
        ])
        
        return workflow_data
    finally:
        db.close()

def get_agent_metrics():
    """Get metrics for agents."""
    db = Session()
    try:
        # Get agent statistics
        sessions = db.query(AgentSession).all()
        
        # Convert to DataFrame
        agent_data = pd.DataFrame([
            {
                'agent_name': s.agent_name,
                'status': s.status,
                'last_active': s.last_active,
                'session_duration': (s.last_active - s.created_at).total_seconds()
            }
            for s in sessions
        ])
        
        return agent_data
    finally:
        db.close()

def get_task_metrics():
    """Get metrics for workflow tasks."""
    db = Session()
    try:
        # Get task statistics
        tasks = db.query(WorkflowTask).all()
        
        # Convert to DataFrame
        task_data = pd.DataFrame([
            {
                'agent_name': t.agent_name,
                'status': t.status,
                'duration': (t.completed_at - t.started_at).total_seconds() if t.completed_at and t.started_at else None
            }
            for t in tasks
        ])
        
        return task_data
    finally:
        db.close()

# Streamlit dashboard
st.set_page_config(page_title="Orchestratex Dashboard", layout="wide")

# Sidebar
st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=7))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Main content
st.title("Orchestratex Dashboard")

# Workflow metrics
st.header("Workflow Metrics")
workflow_data = get_workflow_metrics()

if not workflow_data.empty:
    # Workflow status distribution
    st.subheader("Workflow Status Distribution")
    status_counts = workflow_data['status'].value_counts()
    fig = px.pie(values=status_counts.values, names=status_counts.index, title="Workflow Status")
    st.plotly_chart(fig, use_container_width=True)
    
    # Workflow duration distribution
    st.subheader("Workflow Duration")
    fig = px.histogram(workflow_data, x='duration', nbins=30, title="Workflow Duration Distribution")
    st.plotly_chart(fig, use_container_width=True)

# Agent metrics
st.header("Agent Metrics")
agent_data = get_agent_metrics()

if not agent_data.empty:
    # Agent status distribution
    st.subheader("Agent Status Distribution")
    status_counts = agent_data['status'].value_counts()
    fig = px.bar(status_counts, x=status_counts.index, y=status_counts.values, title="Agent Status")
    st.plotly_chart(fig, use_container_width=True)
    
    # Session duration
    st.subheader("Agent Session Duration")
    fig = px.histogram(agent_data, x='session_duration', nbins=30, title="Agent Session Duration")
    st.plotly_chart(fig, use_container_width=True)

# Task metrics
st.header("Task Metrics")
task_data = get_task_metrics()

if not task_data.empty:
    # Task status distribution
    st.subheader("Task Status Distribution")
    status_counts = task_data['status'].value_counts()
    fig = px.bar(status_counts, x=status_counts.index, y=status_counts.values, title="Task Status")
    st.plotly_chart(fig, use_container_width=True)
    
    # Task duration
    st.subheader("Task Duration")
    fig = px.histogram(task_data, x='duration', nbins=30, title="Task Duration Distribution")
    st.plotly_chart(fig, use_container_width=True)

# Real-time metrics
st.header("Real-time Metrics")

# Create placeholders for real-time updates
workflow_count = st.empty()
active_agents = st.empty()

# Update real-time metrics every 5 seconds
def update_metrics():
    db = Session()
    try:
        workflow_count.metric(
            "Active Workflows",
            db.query(Workflow).filter(Workflow.status != "completed").count()
        )
        
        active_agents.metric(
            "Active Agents",
            db.query(AgentSession).filter(AgentSession.status == "active").count()
        )
    finally:
        db.close()

# Run the dashboard
if __name__ == "__main__":
    while True:
        update_metrics()
        time.sleep(5)
