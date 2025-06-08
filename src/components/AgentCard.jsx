import React from 'react';
import {
  UserCircle,
  Code,
  BookOpen,
  Headphones,
  Eye,
  Shield,
  BarChart2
} from 'lucide-react';
import './AgentCard.css';

const agentIcons = {
  planner: UserCircle,
  rag_maestro: BookOpen,
  code_architect: Code,
  voice_agent: Headphones,
  vision_agent: Eye,
  security_agent: Shield,
  analytics_agent: BarChart2
};

export const AgentCard = ({ agent, isSelected, onSelect }) => {
  const Icon = agentIcons[agent.role] || UserCircle;
  const [isHovered, setIsHovered] = React.useState(false);

  return (
    <div
      className={`agent-card ${isSelected ? 'selected' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onSelect(agent)}
    >
      <div className="agent-header">
        <Icon size={40} className="agent-icon" />
        <h3>{agent.name}</h3>
      </div>
      <div className="agent-body">
        <p className="agent-role">{agent.role}</p>
        <div className="agent-skills">
          {agent.skills.map((skill, index) => (
            <span key={index} className="skill-tag">
              {skill}
            </span>
          ))}
        </div>
        <div className="agent-status">
          <span className={`status-dot ${agent.status}`} />
          <span className="status-text">{agent.status}</span>
        </div>
      </div>
      {isHovered && (
        <div className="agent-hover">
          <p className="hover-description">{agent.description}</p>
          <div className="hover-actions">
            <button onClick={() => onSelect(agent)}>Select</button>
            <button onClick={() => window.open(`/agents/${agent.id}/configure`) }>
              Configure
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
