import React, { useState, useEffect } from 'react';
import { useDagre } from 'react-dagre';
import './WorkflowCanvas.css';

const nodeTypes = {
  START: 'start',
  END: 'end',
  DECISION: 'decision',
  ACTION: 'action',
  AGENT: 'agent',
  CONDITION: 'condition'
};

const nodeColors = {
  start: '#4caf50',
  end: '#f44336',
  decision: '#2196f3',
  action: '#667eea',
  agent: '#9c27b0',
  condition: '#ff9800'
};

export const WorkflowCanvas = ({ workflow, onNodeClick }) => {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const dagre = useDagre();

  useEffect(() => {
    if (workflow) {
      const { nodes: dagNodes, edges: dagEdges } = createDAG(workflow);
      setNodes(dagNodes);
      setEdges(dagEdges);
    }
  }, [workflow]);

  const createDAG = (workflow) => {
    const nodes = [];
    const edges = [];

    // Create nodes
    workflow.nodes.forEach(node => {
      nodes.push({
        id: node.id,
        label: node.label,
        type: node.type,
        x: node.x || 0,
        y: node.y || 0,
        style: {
          fill: nodeColors[node.type],
          stroke: '#fff',
          strokeWidth: 2
        }
      });
    });

    // Create edges
    workflow.edges.forEach(edge => {
      edges.push({
        id: `${edge.source}->${edge.target}`,
        source: edge.source,
        target: edge.target,
        style: {
          stroke: '#666',
          strokeWidth: 2
        }
      });
    });

    return { nodes, edges };
  };

  const handleNodeClick = (nodeId) => {
    if (onNodeClick) {
      onNodeClick(nodeId);
    }
  };

  return (
    <div className="workflow-canvas">
      <svg width="100%" height="100%" viewBox={`0 0 ${dagre.width} ${dagre.height}`}>
        {/* Render edges */}
        {edges.map(edge => (
          <path
            key={edge.id}
            d={dagre.getEdgePath(edge)}
            stroke={edge.style.stroke}
            strokeWidth={edge.style.strokeWidth}
            fill="none"
          />
        ))}

        {/* Render nodes */}
        {nodes.map(node => (
          <g
            key={node.id}
            className="workflow-node"
            onClick={() => handleNodeClick(node.id)}
          >
            <rect
              x={node.x}
              y={node.y}
              width={dagre.getNodeWidth(node)}
              height={dagre.getNodeHeight(node)}
              fill={node.style.fill}
              stroke={node.style.stroke}
              strokeWidth={node.style.strokeWidth}
              rx={node.type === nodeTypes.DECISION ? 0 : 8}
            />
            <text
              x={node.x + dagre.getNodeWidth(node) / 2}
              y={node.y + dagre.getNodeHeight(node) / 2}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="white"
              fontSize="12"
            >
              {node.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
};
