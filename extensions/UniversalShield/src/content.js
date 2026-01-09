/**
 * LinkedIn ScamShield - Content Script
 * 100% Open Source - MIT License
 * 
 * This script runs on LinkedIn pages and scans messages for scams
 */

(function() {
  'use strict';

  // Initialize detector
  const detector = new ScamDetector();
  
  // Stats tracking
  let stats = {
    scansToday: 0,
    scamsBlocked: 0,
    suspiciousFound: 0
  };

  // Load stats from storage
  chrome.storage.local.get(['scamshield_stats'], (result) => {
    if (result.scamshield_stats) {
      stats = result.scamshield_stats;
    }
  });

  /**
   * Create warning badge element
   */
  function createBadge(riskLevel, riskScore) {
    const badge = document.createElement('div');
    badge.className = `scamshield-badge scamshield-${riskLevel}`;
    
    if (riskLevel === 'scam') {
      badge.innerHTML = `
        <span class="scamshield-icon">🚨</span>
        <span class="scamshield-text">SCAM ALERT (${riskScore}%)</span>
      `;
    } else if (riskLevel === 'suspicious') {
      badge.innerHTML = `
        <span class="scamshield-icon">⚠️</span>
        <span class="scamshield-text">Suspicious (${riskScore}%)</span>
      `;
    }
    
    return badge;
  }

  /**
   * Create detailed tooltip
   */
  function createTooltip(analysis) {
    const tooltip = document.createElement('div');
    tooltip.className = 'scamshield-tooltip';
    
    let categoriesHtml = analysis.categories
      .map(cat => `<li>${detector.getCategoryName(cat)}</li>`)
      .join('');
    
    let patternsHtml = analysis.matchedPatterns
      .slice(0, 5)
      .map(p => `<li>"${p}"</li>`)
      .join('');
    
    let recommendationsHtml = analysis.recommendations
      .map(r => `<li>${r}</li>`)
      .join('');

    tooltip.innerHTML = `
      <div class="scamshield-tooltip-header">
        🛡️ ScamShield Analysis
      </div>
      <div class="scamshield-tooltip-body">
        <div class="scamshield-tooltip-section">
          <strong>Risk Score:</strong> ${analysis.riskScore}%
        </div>
        <div class="scamshield-tooltip-section">
          <strong>Detected:</strong>
          <ul>${categoriesHtml}</ul>
        </div>
        <div class="scamshield-tooltip-section">
          <strong>Matched Patterns:</strong>
          <ul>${patternsHtml}</ul>
          ${analysis.matchedPatterns.length > 5 ? `<em>+${analysis.matchedPatterns.length - 5} more</em>` : ''}
        </div>
        <div class="scamshield-tooltip-section">
          <strong>Recommendations:</strong>
          <ul>${recommendationsHtml}</ul>
        </div>
      </div>
      <div class="scamshield-tooltip-footer">
        <button class="scamshield-report-btn">Report Scam</button>
        <button class="scamshield-dismiss-btn">Dismiss</button>
      </div>
    `;

    return tooltip;
  }

  /**
   * Scan a message element
   */
  function scanMessage(messageElement) {
    // Skip if already scanned
    if (messageElement.dataset.scamshieldScanned) {
      return;
    }
    messageElement.dataset.scamshieldScanned = 'true';

    // Get message text
    const messageText = messageElement.innerText || messageElement.textContent;
    if (!messageText || messageText.length < 20) {
      return;
    }

    // Analyze message
    const analysis = detector.analyzeMessage(messageText);
    stats.scansToday++;

    // If suspicious or scam, add badge
    if (analysis.riskLevel !== 'safe') {
      const badge = createBadge(analysis.riskLevel, analysis.riskScore);
      const tooltip = createTooltip(analysis);
      
      // Add badge to message
      messageElement.style.position = 'relative';
      messageElement.appendChild(badge);
      messageElement.appendChild(tooltip);

      // Show tooltip on badge click
      badge.addEventListener('click', (e) => {
        e.stopPropagation();
        tooltip.classList.toggle('scamshield-tooltip-visible');
      });

      // Handle report button
      tooltip.querySelector('.scamshield-report-btn')?.addEventListener('click', () => {
        reportScam(messageText, analysis);
      });

      // Handle dismiss button
      tooltip.querySelector('.scamshield-dismiss-btn')?.addEventListener('click', () => {
        badge.remove();
        tooltip.remove();
      });

      // Update stats
      if (analysis.riskLevel === 'scam') {
        stats.scamsBlocked++;
      } else {
        stats.suspiciousFound++;
      }

      // Highlight message
      messageElement.classList.add(`scamshield-highlight-${analysis.riskLevel}`);
    }

    // Save stats
    chrome.storage.local.set({ scamshield_stats: stats });
  }

  /**
   * Report a scam (sends to background script)
   */
  function reportScam(messageText, analysis) {
    chrome.runtime.sendMessage({
      type: 'REPORT_SCAM',
      data: {
        messageText: messageText.substring(0, 500),
        analysis: analysis,
        url: window.location.href,
        timestamp: new Date().toISOString()
      }
    });
    alert('Thank you for reporting! This helps protect the community.');
  }

  /**
   * Scan all messages on page
   */
  function scanAllMessages() {
    // LinkedIn messaging selectors
    const selectors = [
      '.msg-s-message-list__event',
      '.msg-s-event__content',
      '.message-body',
      '.msg-s-event-listitem__body',
      '.invitation-card__custom-message',
      '.invitation-card__message-content',
      '[data-test-message-text-body]'
    ];

    selectors.forEach(selector => {
      document.querySelectorAll(selector).forEach(scanMessage);
    });
  }

  /**
   * Set up mutation observer to detect new messages
   */
  function setupObserver() {
    const observer = new MutationObserver((mutations) => {
      let shouldScan = false;
      
      mutations.forEach((mutation) => {
        if (mutation.addedNodes.length > 0) {
          shouldScan = true;
        }
      });

      if (shouldScan) {
        // Debounce scanning
        clearTimeout(window.scamshieldScanTimeout);
        window.scamshieldScanTimeout = setTimeout(scanAllMessages, 500);
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  /**
   * Initialize ScamShield
   */
  function init() {
    console.log('🛡️ LinkedIn ScamShield initialized');
    
    // Initial scan
    setTimeout(scanAllMessages, 1000);
    
    // Set up observer for new messages
    setupObserver();

    // Re-scan periodically (for dynamic content)
    setInterval(scanAllMessages, 5000);
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
