import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Globe,
  AlertCircle,
  CheckCircle2,
  Loader2
} from 'lucide-react';

const LANGUAGES = [
  { code: 'en-US', name: 'English', flag: '🇺🇸' },
  { code: 'zh-CN', name: 'Mandarin', flag: '🇨🇳' },
  { code: 'hi-IN', name: 'Hindi', flag: '🇮🇳' },
  { code: 'es-ES', name: 'Spanish', flag: '🇪🇸' },
  { code: 'fr-FR', name: 'French', flag: '🇫🇷' },
  { code: 'ar-SA', name: 'Arabic', flag: '🇸🇦' },
  { code: 'bn-BD', name: 'Bengali', flag: '🇧🇩' },
  { code: 'pt-BR', name: 'Portuguese', flag: '🇧🇷' },
  { code: 'ru-RU', name: 'Russian', flag: '🇷🇺' },
  { code: 'ja-JP', name: 'Japanese', flag: '🇯🇵' },
  { code: 'de-DE', name: 'German', flag: '🇩🇪' },
  { code: 'ur-PK', name: 'Urdu', flag: '🇵🇰' }
];

const LanguageSelector = ({ 
  selectedLanguage, 
  onSelect,
  isLoading,
  error
}) => {
  return (
    <motion.div 
      className="language-selector"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="selector-header">
        <Globe size={20} />
        <span>Select Language</span>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            className="error-toast"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <AlertCircle size={16} />
            <span>{error}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="language-grid">
        {LANGUAGES.map((lang) => (
          <motion.button
            key={lang.code}
            className={`language-button ${selectedLanguage === lang.code ? 'selected' : ''}`}
            onClick={() => onSelect(lang.code)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            disabled={isLoading}
          >
            <span className="flag">{lang.flag}</span>
            <span className="language-name">{lang.name}</span>
            {selectedLanguage === lang.code && (
              <CheckCircle2 size={16} className="selected-icon" />
            )}
          </motion.button>
        ))}
      </div>

      <AnimatePresence>
        {isLoading && (
          <motion.div
            className="loading-indicator"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <Loader2 size={20} className="loading-spinner" />
            <span>Loading...</span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default LanguageSelector;
