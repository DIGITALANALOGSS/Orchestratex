import React from 'react';
import './BrandedLayout.css';

export const BrandedLayout = ({ children }) => {
  return (
    <div className="orchestratex-app">
      <header className="app-header">
        <img src="/assets/mckown-logo.png" alt="McKown Media Solutions" className="brand-logo" />
        <h1>OrchestrateX</h1>
        <nav className="main-nav">
          <a href="/dashboard">Dashboard</a>
          <a href="/agents">Agents</a>
          <a href="/workflows">Workflows</a>
          <a href="/voice-agent">Voice AI</a>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
};
