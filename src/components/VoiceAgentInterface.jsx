import React, { useState, useEffect } from 'react';
import './VoiceAgentInterface.css';
import VoiceControls from './VoiceControls';
import AgentStatus from './AgentStatus';
import ConversationDisplay from './ConversationDisplay';

export const VoiceAgentInterface = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [emotion, setEmotion] = useState(null);
  const [conversation, setConversation] = useState([]);

  useEffect(() => {
    // Initialize WebSocket connection for real-time updates
    const ws = new WebSocket('ws://localhost:8000/ws/voice-agent');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'emotion') {
        setEmotion(data.emotion);
      } else if (data.type === 'transcript') {
        setConversation(prev => [...prev, {
          text: data.text,
          isUser: data.isUser,
          timestamp: new Date().toISOString()
        }]);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="voice-agent-interface">
      <div className="voice-controls-overlay">
        <VoiceControls 
          isRecording={isRecording}
          onToggleRecording={() => setIsRecording(!isRecording)}
        />
        <AgentStatus emotion={emotion} />
        <ConversationDisplay conversation={conversation} />
      </div>
    </div>
  );
};
