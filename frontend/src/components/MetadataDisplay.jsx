/**
 * MetadataDisplay Component
 * Shows enhanced information about message routing, safety, and session details
 */

import React, { useState } from 'react';
import { METADATA_LABELS } from '../utils/constants';

const MetadataDisplay = ({ 
  metadata, 
  show = false, 
  className = '',
  compact = false 
}) => {
  const [expanded, setExpanded] = useState(false);

  if (!metadata || !show) {
    return null;
  }

  const {
    routing_info,
    safety_info,
    session_id,
    project_id,
    sources = []
  } = metadata;

  const formatRoutingInfo = (info) => {
    if (!info) return null;
    
    const decision = info.decision || 'unknown';
    const confidence = info.confidence || 0;
    const label = METADATA_LABELS.ROUTING[decision] || decision;
    
    return {
      label,
      confidence,
      decision,
      color: getRoutingColor(decision)
    };
  };

  const formatSafetyInfo = (info) => {
    if (!info) return null;
    
    const level = info.level || info.safety_level || 'unknown';
    const confidence = info.confidence || 0;
    const label = METADATA_LABELS.SAFETY[level] || level;
    
    return {
      label,
      confidence,
      level,
      color: getSafetyColor(level),
      patterns: info.pattern_matches || []
    };
  };

  const getRoutingColor = (decision) => {
    const colors = {
      'kb_only': '#3b82f6',           // blue
      'memory_only': '#8b5cf6',       // purple  
      'kb_and_memory': '#10b981',     // green
      'sensitive_handling': '#f59e0b', // amber
      'default': '#6b7280'            // gray
    };
    return colors[decision] || colors.default;
  };

  const getSafetyColor = (level) => {
    const colors = {
      'safe': '#10b981',              // green
      'potentially_sensitive': '#f59e0b', // amber
      'sensitive': '#ef4444',         // red
      'harmful': '#dc2626'            // dark red
    };
    return colors[level] || colors.safe;
  };

  const routingData = formatRoutingInfo(routing_info);
  const safetyData = formatSafetyInfo(safety_info);

  if (compact) {
    return (
      <div className={`metadata-display compact ${className}`}>
        <div className="metadata-compact">
          {routingData && (
            <span 
              className="routing-badge"
              style={{ backgroundColor: routingData.color }}
              title={`Routing: ${routingData.label} (${(routingData.confidence * 100).toFixed(0)}%)`}
            >
              {routingData.label}
            </span>
          )}
          {safetyData && safetyData.level !== 'safe' && (
            <span 
              className="safety-badge"
              style={{ backgroundColor: safetyData.color }}
              title={`Safety: ${safetyData.label} (${(safetyData.confidence * 100).toFixed(0)}%)`}
            >
              {safetyData.label}
            </span>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className={`metadata-display ${expanded ? 'expanded' : ''} ${className}`}>
      <div className="metadata-header">
        <span className="metadata-title">Response Details</span>
        <button
          onClick={() => setExpanded(!expanded)}
          className="metadata-toggle"
          aria-label={expanded ? 'Hide details' : 'Show details'}
        >
          {expanded ? '−' : '+'}
        </button>
      </div>

      {expanded && (
        <div className="metadata-content">
          {/* Routing Information */}
          {routingData && (
            <div className="metadata-section">
              <h5>Routing Decision</h5>
              <div className="routing-info">
                <span 
                  className="routing-label"
                  style={{ color: routingData.color }}
                >
                  {routingData.label}
                </span>
                <span className="confidence-score">
                  Confidence: {(routingData.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="routing-description">
                {getRoutingDescription(routingData.decision)}
              </div>
            </div>
          )}

          {/* Safety Information */}
          {safetyData && (
            <div className="metadata-section">
              <h5>Content Safety</h5>
              <div className="safety-info">
                <span 
                  className="safety-label"
                  style={{ color: safetyData.color }}
                >
                  {safetyData.label}
                </span>
                <span className="confidence-score">
                  Confidence: {(safetyData.confidence * 100).toFixed(1)}%
                </span>
              </div>
              {safetyData.patterns.length > 0 && (
                <div className="safety-patterns">
                  <span className="patterns-label">Detected patterns:</span>
                  <ul className="patterns-list">
                    {safetyData.patterns.map((pattern, index) => (
                      <li key={index} className="pattern-item">{pattern}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Session Information */}
          {(session_id || project_id) && (
            <div className="metadata-section">
              <h5>Session Details</h5>
              <div className="session-info">
                {session_id && (
                  <div className="session-detail">
                    <span className="detail-label">Session:</span>
                    <span className="detail-value" title={session_id}>
                      {session_id.slice(0, 8)}...
                    </span>
                  </div>
                )}
                {project_id && (
                  <div className="session-detail">
                    <span className="detail-label">Project:</span>
                    <span className="detail-value">{project_id}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Sources */}
          {sources.length > 0 && (
            <div className="metadata-section">
              <h5>Knowledge Sources</h5>
              <ul className="sources-list">
                {sources.map((source, index) => (
                  <li key={index} className="source-item">
                    {source}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const getRoutingDescription = (decision) => {
  const descriptions = {
    'kb_only': 'Used knowledge base documents only',
    'memory_only': 'Used conversation memory only',
    'kb_and_memory': 'Combined knowledge base and conversation memory',
    'sensitive_handling': 'Applied special handling for sensitive content',
    'default': 'Standard processing applied'
  };
  return descriptions[decision] || 'Unknown routing decision';
};

export default MetadataDisplay;