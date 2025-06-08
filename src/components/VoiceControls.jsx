import React from 'react';
import './VoiceControls.css';

export const VoiceControls = ({ isRecording, onToggleRecording }) => {
  return (
    <div className="voice-controls">
      <button 
        className={`record-btn ${isRecording ? 'recording' : ''}`} 
        onClick={onToggleRecording}
      >
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
      <div className="control-options">
        <button className="option-btn">Microphone Settings</button>
        <button className="option-btn">Language</button>
        <button className="option-btn">Voice Profile</button>
      </div>
    </div>
  );
};
