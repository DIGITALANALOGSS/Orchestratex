import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Clock, ArrowRight, Star, AlertCircle } from 'lucide-react';
import './OnboardingFlow.css';

export const OnboardingFlow = ({ userId }) => {
  const [progress, setProgress] = useState(null);
  const [currentSteps, setCurrentSteps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    loadOnboardingData();
  }, [userId]);

  const loadOnboardingData = async () => {
    try {
      const [progressData, stepsData] = await Promise.all([
        fetch(`/api/onboarding/progress/${userId}`).then(r => r.json()),
        fetch(`/api/onboarding/current-steps/${userId}`).then(r => r.json())
      ]);
      setProgress(progressData);
      setCurrentSteps(stepsData);
    } catch (error) {
      console.error('Failed to load onboarding data:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeStep = async (stepId) => {
    try {
      await fetch(`/api/onboarding/complete-step`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, stepId })
      });
      await loadOnboardingData(); // Refresh data
    } catch (error) {
      console.error('Failed to complete step:', error);
    }
  };

  if (loading) return <OnboardingLoader />;

  return (
    <div className="onboarding-container">
      <OnboardingHeader progress={progress} />
      <ProgressBar percentage={progress.progress_percentage} />
      <StepsGrid 
        steps={currentSteps} 
        onCompleteStep={completeStep}
        showSuccess={showSuccess}
        setShowSuccess={setShowSuccess}
      />
      <OnboardingFooter progress={progress} />
    </div>
  );
};

const OnboardingHeader = ({ progress }) => (
  <motion.div 
    className="onboarding-header"
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <h1>Welcome to OrchestrateX</h1>
    <p>Let's get your AI orchestration platform set up in just a few steps</p>
    <div className="stage-indicator">
      <span className="current-stage">{progress.current_stage}</span>
      <div className="time-remaining">
        <Clock size={16} />
        {progress.estimated_time_remaining} min remaining
      </div>
    </div>
  </motion.div>
);

const ProgressBar = ({ percentage }) => (
  <div className="progress-container">
    <div className="progress-bar">
      <motion.div 
        className="progress-fill"
        initial={{ width: 0 }}
        animate={{ width: `${percentage}%` }}
        transition={{ duration: 0.5 }}
      >
        <span className="progress-label">{Math.round(percentage)}% Complete</span>
      </motion.div>
    </div>
  </div>
);

const StepsGrid = ({ steps, onCompleteStep, showSuccess, setShowSuccess }) => (
  <div className="steps-grid">
    <AnimatePresence>
      {steps.map((step, index) => (
        <motion.div
          key={step.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{ delay: index * 0.1 }}
        >
          <StepCard 
            step={step} 
            onComplete={onCompleteStep}
            showSuccess={showSuccess}
            setShowSuccess={setShowSuccess}
          />
        </motion.div>
      ))}
    </AnimatePresence>
  </div>
);

const StepCard = ({ step, onComplete, showSuccess, setShowSuccess }) => {
  const [isCompleting, setIsCompleting] = useState(false);
  const [error, setError] = useState(null);

  const handleComplete = async () => {
    setIsCompleting(true);
    setError(null);
    try {
      await onComplete(step.id);
      setShowSuccess(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsCompleting(false);
    }
  };

  return (
    <div className={`step-card ${step.required ? 'required' : 'optional'}`}>
      <div className="step-header">
        <h3>{step.title}</h3>
        {step.required && <Star size={16} className="required-icon" />}
      </div>
      <p className="step-description">{step.description}</p>
      <div className="step-meta">
        <span className="estimated-time">
          <Clock size={14} />
          {step.estimated_time} min
        </span>
        {error && (
          <span className="error-icon">
            <AlertCircle size={16} />
          </span>
        )}
      </div>
      <button 
        className={`step-button ${error ? 'error' : ''}`}
        onClick={handleComplete}
        disabled={isCompleting}
      >
        {isCompleting ? (
          <span className="loading">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </span>
        ) : (
          <>
            {error ? 'Try Again' : 'Start Step'}
            <ArrowRight size={16} />
          </>
        )}
      </button>
      {showSuccess && (
        <motion.div 
          className="success-banner"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <CheckCircle size={24} className="success-icon" />
          <span>Step completed successfully!</span>
        </motion.div>
      )}
    </div>
  );
};

const OnboardingFooter = ({ progress }) => {
  const isLastStep = progress.current_stage === 'production_ready';
  
  return (
    <div className="onboarding-footer">
      <div className="footer-content">
        <p>Need help? Check our <a href="/docs">documentation</a> or contact support.</p>
        {isLastStep && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="congratulations">
              <h3>🎉 Congratulations!</h3>
              <p>Your OrchestrateX platform is now ready to use!</p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};
