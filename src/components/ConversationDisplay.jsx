import React from 'react';
import './ConversationDisplay.css';

export const ConversationDisplay = ({ conversation }) => {
  return (
    <div className="conversation-display">
      <div className="messages-container">
        {conversation.map((message, index) => (
          <div 
            key={index}
            className={`message ${message.isUser ? 'user' : 'agent'}`}
          >
            <div className="message-content">
              <div className="message-text">{message.text}</div>
              <div className="message-meta">
                <span className="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
