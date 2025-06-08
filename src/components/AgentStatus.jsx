import React from 'react';
import './AgentStatus.css';

const EMOTION_COLORS = {
  happy: '#4CAF50',
  sad: '#2196F3',
  angry: '#f44336',
  neutral: '#9E9E9E',
  excited: '#FF9800',
  confused: '#9C27B0',
  default: '#607D8B'
};

export const AgentStatus = ({ emotion }) => {
  const status = emotion || { state: 'ready', emotion: 'neutral', confidence: 0.8 };
  
  return (
    <div className="agent-status">
      <div className="status-circle" style={{
        backgroundColor: EMOTION_COLORS[status.emotion] || EMOTION_COLORS.default
      }}>
        <span className="status-indicator"></span>
      </div>
      <div className="status-info">
        <h3>Agent Status</h3>
        <p>Current State: {status.state}</p>
        <p>Detected Emotion: {status.emotion}</p>
        <p>Confidence: {(status.confidence * 100).toFixed(1)}%</p>
      </div>
    </div>
  );
};
