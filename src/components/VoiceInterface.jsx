import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Microphone,
  Speaker,
  Globe,
  AlertCircle,
  Loader2,
  CheckCircle2
} from 'lucide-react';
import LanguageSelector from './LanguageSelector';
import { getEmotionIcon } from './emotionIcons';
import './VoiceInterface.css';

const VoiceInterface = () => {
  const [language, setLanguage] = useState('en-US');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [emotion, setEmotion] = useState({
    happiness: 0,
    sadness: 0,
    anger: 0,
    surprise: 0,
    fear: 0,
    disgust: 0,
    neutral: 0
  });
  const [activeEmotion, setActiveEmotion] = useState('neutral');

  // Update active emotion when emotion changes
  useEffect(() => {
    if (Object.keys(emotion).length > 0) {
      const maxEmotion = Object.entries(emotion)
        .reduce((a, b) => a[1] > b[1] ? a : b)[0];
      setActiveEmotion(maxEmotion);
    }
  }, [emotion]);

  // Animate emotion bars
  useEffect(() => {
    const animateBars = () => {
      Object.values(document.querySelectorAll('.emotion-fill')).forEach(bar => {
        const targetWidth = parseFloat(bar.dataset.target) || 0;
        const currentWidth = parseFloat(bar.style.width) || 0;
        
        if (Math.abs(targetWidth - currentWidth) > 0.5) {
          bar.style.width = `${currentWidth + (targetWidth - currentWidth) * 0.2}px`;
          requestAnimationFrame(animateBars);
        }
      });
    };
    
    animateBars();
  }, [emotion]);

  const handleLanguageChange = async (newLanguage) => {
    try {
      setIsLoading(true);
      setError(null);
      await setLanguage(newLanguage);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartListening = async () => {
    try {
      setIsListening(true);
      setError(null);
      
      // Initialize recording
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Send start recording message
      await fetch('/api/voice/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          language,
          userId: localStorage.getItem('userId')
        })
      });
    } catch (err) {
      setError('Failed to start listening: ' + err.message);
    }
  };

  const handleStopListening = async () => {
    try {
      setIsListening(false);
      
      // Stop recording
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      
      // Send stop recording message
      await fetch('/api/voice/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: localStorage.getItem('userId')
        })
      });
    } catch (err) {
      setError('Failed to stop listening: ' + err.message);
    }
  };

  // Handle incoming messages from WebSocket
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/voice/${localStorage.getItem('userId')}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'transcription') {
        setConversation(prev => [...prev, {
          text: data.text,
          isUser: true,
          timestamp: new Date().toISOString(),
          language: data.language
        }]);
      } else if (data.type === 'response') {
        setConversation(prev => [...prev, {
          text: data.text,
          isUser: false,
          timestamp: new Date().toISOString(),
          language: data.language
        }]);
      } else if (data.type === 'emotion') {
        setEmotion(data.emotion);
      } else if (data.type === 'error') {
        setError(data.message);
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div className="voice-interface">
      <LanguageSelector
        selectedLanguage={language}
        onSelect={handleLanguageChange}
        isLoading={isLoading}
        error={error}
      />

      <div className="voice-controls">
        <AnimatePresence>
          {isListening && (
            <motion.div 
              className="listening-indicator"
              initial={{ scale: 0.8 }}
              animate={{ scale: 1.2 }}
              exit={{ scale: 0.8 }}
              transition={{
                repeat: Infinity,
                duration: 1,
                ease: "easeInOut"
              }}
            >
              <Loader2 className="listening-spinner" />
              <span>Listening...</span>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.button
          className="mic-button"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => isListening ? handleStopListening() : handleStartListening()}
        >
          <Microphone size={24} className={isListening ? 'listening' : ''} />
        </motion.button>

        <div className="language-badge">
          <Globe size={16} />
          <span>{language.split('-')[0].toUpperCase()}</span>
        </div>
      </div>

      <div className="conversation-panel">
        {conversation.map((message, index) => (
          <motion.div
            key={index}
            className={`message ${message.isUser ? 'user' : 'agent'}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="message-content">
              <span className="message-text">{message.text}</span>
              <div className="message-meta">
                <span className="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
                <span className="language">{message.language.split('-')[0].toUpperCase()}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="emotion-panel">
        <AnimatePresence>
          {Object.keys(emotion).length > 0 && (
            <motion.div
              className="emotion-display"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="emotion-label">Emotional State</div>
              <div className="emotion-values">
                {Object.entries(emotion).map(([emotion, value]) => (
                  <motion.div
                    key={emotion}
                    className={`emotion-item ${activeEmotion === emotion ? 'active' : ''}`}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                      // Play emotion-specific sound effect
                      const audio = new Audio(`sounds/${emotion}.mp3`);
                      audio.play();
                    }}
                  >
                    <div className="emotion-icon">
                      {getEmotionIcon(emotion)}
                    </div>
                    <div className="emotion-name">{emotion}</div>
                    <div className="emotion-bar-container">
                      <div 
                        className="emotion-fill"
                        data-target={`${value * 100}%`}
                        style={{ width: '0%' }}
                      />
                    </div>
                    <div className="emotion-value">
                      {value.toFixed(2)}
                      <span className="confidence-label">Confidence</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default VoiceInterface;
