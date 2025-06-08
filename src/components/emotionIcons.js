import {
  Smile,
  Frown,
  Angry,
  Zap,
  AlertTriangle,
  Meh,
  FaceNeutral
} from 'lucide-react';

export const getEmotionIcon = (emotion) => {
  const icons = {
    happiness: <Smile size={24} className="emotion-icon" />,
    sadness: <Frown size={24} className="emotion-icon" />,
    anger: <Angry size={24} className="emotion-icon" />,
    surprise: <Zap size={24} className="emotion-icon" />,
    fear: <AlertTriangle size={24} className="emotion-icon" />,
    disgust: <Meh size={24} className="emotion-icon" />,
    neutral: <FaceNeutral size={24} className="emotion-icon" />
  };

  return icons[emotion] || icons.neutral;
};
