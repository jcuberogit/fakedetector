/**
 * Visual Badge System - Frictionless UX
 * 
 * 🟢 GREEN: Safe (score < 30) - No interruption
 * 🟡 YELLOW: Caution (score 30-70) - Subtle warning
 * 🔴 RED: Critical (score > 70) - Clear alert
 */

class ShieldBadge {
  constructor() {
    this.container = null;
  }
  
  render(analysis, messageElement) {
    const badge = document.createElement('div');
    badge.className = `universalshield-badge ${analysis.risk_level}`;
    
    badge.innerHTML = `
      <span class="shield-icon">${this.getIcon(analysis.risk_level)}</span>
      <span class="risk-label">${this.getLabel(analysis.risk_level)}</span>
      <button class="details-btn" title="Why?">?</button>
    `;
    
    // Position badge near message
    messageElement.style.position = 'relative';
    messageElement.appendChild(badge);
    
    // Add click handler for explanation
    badge.querySelector('.details-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      this.showExplanation(analysis);
    });
    
    return badge;
  }
  
  getIcon(level) {
    const icons = {
      'safe': '🛡️',
      'caution': '⚠️',
      'critical': '🚨'
    };
    return icons[level] || '🛡️';
  }
  
  getLabel(level) {
    const labels = {
      'safe': 'Safe',
      'caution': 'Caution',
      'critical': 'RISK'
    };
    return labels[level] || 'Unknown';
  }
  
  showExplanation(analysis) {
    // Remove existing modal if any
    const existingModal = document.querySelector('.universalshield-modal');
    if (existingModal) {
      existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.className = 'universalshield-modal';
    modal.innerHTML = `
      <div class="modal-content">
        <h3>${this.getIcon(analysis.risk_level)} Risk Analysis</h3>
        <div class="risk-score">
          <span class="score">${analysis.risk_score}</span>/100
        </div>
        <div class="risk-level-badge ${analysis.risk_level}">
          ${this.getLabel(analysis.risk_level).toUpperCase()}
        </div>
        <div class="explanation">
          <h4>Why this was flagged:</h4>
          <p>${analysis.explanation}</p>
        </div>
        ${this.renderSignals(analysis.context_signals)}
        <div class="source-info">
          <small>Analysis: ${analysis.source === 'local' ? '100% Local (Private)' : 'Cloud ML'} | Tier: ${analysis.tier || 'Free'}</small>
        </div>
        <div class="actions">
          <button class="report-btn">🚩 Report Scam</button>
          <button class="dismiss-btn">Dismiss</button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Close on background click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.remove();
      }
    });
    
    // Close handlers
    modal.querySelector('.dismiss-btn').addEventListener('click', () => {
      modal.remove();
    });
    
    modal.querySelector('.report-btn').addEventListener('click', () => {
      this.reportScam(analysis);
      modal.remove();
    });
  }
  
  renderSignals(signals) {
    if (!signals) return '';
    
    const items = [];
    
    if (signals.behavioral) {
      const b = signals.behavioral;
      if (b.urgency_level > 0.7) {
        items.push('<li class="warning">⚡ High urgency language detected</li>');
      }
      if (b.file_risk > 0.8) {
        items.push(`<li class="danger">📁 Dangerous file type: ${b.file_type}</li>`);
      }
      if (b.requests_credentials) {
        items.push('<li class="danger">🔑 Requests login credentials</li>');
      }
      if (b.requests_money) {
        items.push('<li class="danger">💰 Requests money transfer</li>');
      }
      if (b.suspicious_links) {
        items.push('<li class="warning">🔗 Suspicious links detected</li>');
      }
    }
    
    if (signals.social) {
      const s = signals.social;
      if (s.account_age_days < 7) {
        items.push(`<li class="warning">👤 Very new account (${s.account_age_days} days old)</li>`);
      } else if (s.account_age_days < 30) {
        items.push(`<li class="info">👤 New account (${s.account_age_days} days old)</li>`);
      }
      if (s.connection_degree > 2) {
        items.push('<li class="warning">🔗 No direct connection to sender</li>');
      }
      if (s.previous_interactions === 0) {
        items.push('<li class="info">✉️ First time contact</li>');
      }
    }
    
    if (signals.linguistic) {
      const l = signals.linguistic;
      if (l.excessive_punctuation) {
        items.push('<li class="warning">❗ Excessive punctuation (spam indicator)</li>');
      }
      if (l.all_caps_ratio > 0.3) {
        items.push('<li class="warning">🔤 Excessive capital letters</li>');
      }
    }
    
    if (items.length === 0) {
      return '<div class="signals"><p>No specific warning signals detected.</p></div>';
    }
    
    return `
      <div class="signals">
        <h4>Detected Signals:</h4>
        <ul>${items.join('')}</ul>
      </div>
    `;
  }
  
  async reportScam(analysis) {
    try {
      // Create pattern hash (no raw content)
      const patternHash = this.createPatternHash(analysis);
      
      const response = await fetch('https://api.universalshield.dev/api/v1/report-scam', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pattern_hash: patternHash,
          category: this.categorizeScam(analysis),
          risk_score: analysis.risk_score
        })
      });
      
      if (response.ok) {
        this.showNotification('✅ Thank you for reporting! This helps protect others.');
      }
    } catch (error) {
      console.error('Failed to report scam:', error);
    }
  }
  
  createPatternHash(analysis) {
    // Create hash from signals, not content
    const signals = analysis.context_signals || {};
    const hashInput = JSON.stringify({
      risk_score: analysis.risk_score,
      behavioral: signals.behavioral,
      social: signals.social
    });
    return btoa(hashInput).substring(0, 32);
  }
  
  categorizeScam(analysis) {
    const signals = analysis.context_signals || {};
    const b = signals.behavioral || {};
    
    if (b.file_risk > 0.8) return 'malware_delivery';
    if (b.requests_credentials) return 'credential_phishing';
    if (b.requests_money) return 'advance_fee_fraud';
    return 'general_scam';
  }
  
  showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'universalshield-notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
}

// Export for use in extension
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ShieldBadge;
}
