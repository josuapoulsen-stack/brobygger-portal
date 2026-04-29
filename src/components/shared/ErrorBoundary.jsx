/**
 * src/components/shared/ErrorBoundary.jsx
 *
 * React error boundary — fanger uventede render-fejl og viser
 * en venlig fejlskærm i stedet for en hvid side.
 *
 * Brug:
 *   <ErrorBoundary>
 *     <MinKomponent />
 *   </ErrorBoundary>
 *
 *   // Med custom fallback:
 *   <ErrorBoundary fallback={<div>Noget gik galt</div>}>
 *     ...
 *   </ErrorBoundary>
 */

import React from 'react';
import { SoS } from '../../styles/tokens';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // I produktion: send til Application Insights
    if (typeof window !== 'undefined' && window.appInsights) {
      window.appInsights.trackException({ exception: error, properties: info });
    }
    console.error('[ErrorBoundary]', error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    if (this.props.fallback) return this.props.fallback;

    return <DefaultFallback error={this.state.error} onReset={this.handleReset} />;
  }
}

function DefaultFallback({ error, onReset }) {
  return (
    <div
      style={{
        display:        'flex',
        flexDirection:  'column',
        alignItems:     'center',
        justifyContent: 'center',
        minHeight:      '60vh',
        padding:        '32px 24px',
        textAlign:      'center',
        background:     SoS.cream,
      }}
    >
      {/* Ikon */}
      <div
        style={{
          width:          64,
          height:         64,
          borderRadius:   '50%',
          background:     SoS.roseSoft,
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'center',
          marginBottom:   20,
        }}
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
          stroke={SoS.rose} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>

      <div style={{ fontFamily: SoS.font, fontSize: 22, fontWeight: 500,
        color: SoS.ink, marginBottom: 8 }}>
        Noget gik galt
      </div>

      <div style={{ fontFamily: SoS.sans, fontSize: 14, color: SoS.inkSoft,
        lineHeight: 1.6, maxWidth: 280, marginBottom: 24 }}>
        Der opstod en uventet fejl. Prøv igen, eller kontakt support hvis problemet fortsætter.
      </div>

      {/* Fejldetalje — kun i dev */}
      {import.meta?.env?.DEV && error?.message && (
        <div style={{
          maxWidth: 320, marginBottom: 20, padding: '10px 14px',
          background: '#fff', borderRadius: SoS.r.sm,
          border: `1px solid ${SoS.roseSoft}`,
          fontFamily: 'monospace', fontSize: 12, color: SoS.rose,
          textAlign: 'left', wordBreak: 'break-all', lineHeight: 1.5,
        }}>
          {error.message}
        </div>
      )}

      <button
        onClick={onReset}
        style={{
          background:   SoS.orange,
          color:        '#fff',
          border:       'none',
          padding:      '10px 24px',
          borderRadius: SoS.r.md,
          fontFamily:   SoS.sans,
          fontSize:     14,
          fontWeight:   600,
          cursor:       'pointer',
          boxShadow:    SoS.shadow.sm,
        }}
      >
        Prøv igen
      </button>
    </div>
  );
}

export default ErrorBoundary;
