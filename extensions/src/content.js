/**
 * JobGuard AI - Content Script
 * 
 * LinkedIn-only protection against job scams and fake recruiters
 */

console.log('🛡️ JobGuard AI content.js loading...');

(function() {
  'use strict';

  try {
    console.log('🛡️ JobGuard AI initialized for LinkedIn');
  
  // Note: LinkedIn generates spam errors (chrome-extension://invalid) - these are from LinkedIn's code, not ours

  // Initialize cloud analyzer (VPS Agent is sole authority)
  let cloudAnalyzer = null;
  let licenseKey = null;

  // Initialize CloudAnalyzer if available
  chrome.storage.local.get(['scamshield_license'], (result) => {
    licenseKey = result.scamshield_license || 'US-PRO-DEMO12345678';
    if (typeof CloudAnalyzer !== 'undefined') {
      cloudAnalyzer = new CloudAnalyzer('https://jobguard.nomadahealth.com', licenseKey);
    }
  });
  
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

  // LinkedIn-only message selectors
  const MESSAGE_SELECTORS = [
    '.msg-s-event-listitem__body', 
    '.msg-s-event-listitem__message-bubble',
    '.msg-s-event__content',
    '.msg-s-message-group__content',
    '.feed-shared-text',
    'div[role="main"] .update-components-text'
  ];

  /**
   * Create warning badge element
   */
  function createBadge(result) {
    const badge = document.createElement('div');
    badge.className = 'scamshield-badge shield-badge';
    
    const badgeText = result.isScam ? '⚠️ JOBGUARD AI: SCAM DETECTED' : '⚠️ JOBGUARD AI: SUSPICIOUS';
    const bgColor = result.isScam ? '#ff0000' : '#ffcc00';

    const badgeInner = document.createElement('div');
    badgeInner.style.cssText = `
      background: ${bgColor};
      color: white;
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 800;
      margin-bottom: 8px;
      display: inline-block;
      z-index: 9999;
      cursor: pointer;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    `;
    badgeInner.title = `Matched: ${result.matchedPatterns.join(', ')}`;
    badgeInner.textContent = badgeText;
    badge.appendChild(badgeInner);
    return badge;
  }

  /**
   * Create detailed tooltip
   */
  function createTooltip(analysis) {
    const tooltip = document.createElement('div');
    tooltip.className = 'scamshield-tooltip';
    
    const header = document.createElement('div');
    header.className = 'scamshield-tooltip-header';
    header.textContent = '🛡️ UniversalShield Agent Analysis';
    
    const closeBtn = document.createElement('button');
    closeBtn.className = 'scamshield-close-btn';
    closeBtn.style.cssText = 'float: right; background: none; border: none; color: white; font-size: 18px; cursor: pointer; padding: 0; margin: 0;';
    closeBtn.textContent = '×';
    header.appendChild(closeBtn);
    
    const body = document.createElement('div');
    body.className = 'scamshield-tooltip-body';
    
    const scoreSection = document.createElement('div');
    scoreSection.className = 'scamshield-tooltip-section';
    const scoreLabel = document.createElement('strong');
    scoreLabel.textContent = 'Agent Trust Score:';
    scoreSection.appendChild(scoreLabel);
    scoreSection.appendChild(document.createTextNode(` ${analysis.riskScore}%`));
    body.appendChild(scoreSection);
    
    const intentSection = document.createElement('div');
    intentSection.className = 'scamshield-tooltip-section';
    const intentLabel = document.createElement('strong');
    intentLabel.textContent = 'Agent Intent:';
    intentSection.appendChild(intentLabel);
    intentSection.appendChild(document.createTextNode(` ${analysis.riskLevel.toUpperCase()}`));
    body.appendChild(intentSection);
    
    const patternsSection = document.createElement('div');
    patternsSection.className = 'scamshield-tooltip-section';
    const patternsLabel = document.createElement('strong');
    patternsLabel.textContent = 'Detected Patterns:';
    patternsSection.appendChild(patternsLabel);
    const patternsList = document.createElement('ul');
    const categories = analysis.categories && analysis.categories.length > 0
      ? analysis.categories
      : ['See AI Explanation below'];
    categories.forEach(cat => {
      const li = document.createElement('li');
      li.textContent = cat;
      patternsList.appendChild(li);
    });
    patternsSection.appendChild(patternsList);
    body.appendChild(patternsSection);
    
    const recsSection = document.createElement('div');
    recsSection.className = 'scamshield-tooltip-section';
    const recsLabel = document.createElement('strong');
    recsLabel.textContent = 'Recommendations:';
    recsSection.appendChild(recsLabel);
    const recsList = document.createElement('ul');
    analysis.recommendations.forEach(r => {
      const li = document.createElement('li');
      li.textContent = r;
      recsList.appendChild(li);
    });
    recsSection.appendChild(recsList);
    body.appendChild(recsSection);
    
    if (analysis.explanation) {
      const explSection = document.createElement('div');
      explSection.className = 'scamshield-tooltip-section';
      const explLabel = document.createElement('strong');
      explLabel.textContent = 'AI Explanation:';
      explSection.appendChild(explLabel);
      const explText = document.createElement('p');
      explText.style.cssText = 'font-size: 11px; color: #666; margin: 4px 0;';
      explText.textContent = analysis.explanation;
      explSection.appendChild(explText);
      body.appendChild(explSection);
    }
    
    const footer = document.createElement('div');
    footer.className = 'scamshield-tooltip-footer';
    const reportBtn = document.createElement('button');
    reportBtn.className = 'scamshield-report-btn';
    reportBtn.textContent = 'Report Scam';
    const dismissBtn = document.createElement('button');
    dismissBtn.className = 'scamshield-dismiss-btn';
    dismissBtn.textContent = 'Not a Scam';
    footer.appendChild(reportBtn);
    footer.appendChild(dismissBtn);
    
    tooltip.appendChild(header);
    tooltip.appendChild(body);
    tooltip.appendChild(footer);

    return tooltip;
  }

  /**
   * Scan a message element
   */
  function scanMessage(messageElement) {
    console.log('🛡️ scanMessage called for element:', messageElement);
    
    // CRITICAL: Mark immediately to prevent race conditions
    if (messageElement.dataset.scamshieldScanned === 'true') {
      console.log('🛡️ Already scanned, skipping');
      return;
    }
    messageElement.dataset.scamshieldScanned = 'true';
    
    // CRITICAL: Only scan RECEIVED messages, not sent messages
    // LinkedIn marks OTHER user messages with 'msg-s-event-listitem--other' class
    const parentListItem = messageElement.closest('.msg-s-event-listitem');
    
    // If we have a parent list item, check if it's from another user
    if (parentListItem) {
      const isFromOtherUser = parentListItem.classList.contains('msg-s-event-listitem--other');
      console.log('🛡️ Is from other user:', isFromOtherUser);
      
      if (!isFromOtherUser) {
        console.log('🛡️ Skipping your own message (only scanning received messages)');
        return;
      }
      
      console.log('🛡️ ✅ Scanning received message from other user');
    } else {
      console.log('🛡️ No parent list item found - scanning anyway');
    }
    
    // Skip if already has badge
    if (messageElement.querySelector('.scamshield-badge') ||
        messageElement.querySelector('.shield-badge')) {
      console.log('🛡️ Badge already exists, skipping');
      return;
    }
    
    // Get message text and validate
    const messageText = messageElement.innerText || messageElement.textContent;
    console.log('🛡️ Message text length:', messageText ? messageText.trim().length : 0);
    
    if (!messageText || messageText.trim().length < 20) {
      console.log('🛡️ Message too short, skipping');
      return;
    }

    console.log('🛡️ ✅ Message passed all checks, analyzing...');
    stats.scansToday++;
    
    // VPS Agent Analysis ONLY - Extension is a thin client/sensor
    if (cloudAnalyzer) {
      performCloudAnalysis(messageElement, messageText);
    } else {
      console.warn('🛡️ UniversalShield: CloudAnalyzer not initialized. VPS Agent required for detection.');
    }
  }

  /**
   * Perform cloud-based ML analysis using the VPS agent
   * VPS Agent is the SOLE AUTHORITY for fraud detection
   */
  async function performCloudAnalysis(messageElement, messageText) {
    try {
      console.log('🛡️ [DEBUG] Step 1: Starting performCloudAnalysis');
      
      // Collect anonymized metadata (no PII)
      const metadata = {
        platform: 'linkedin',
        accountAge: 365, // Default for now, could be extracted from DOM
        connectionDegree: 3,
        hasAttachment: messageText.includes('Download') || messageText.includes('.pdf'),
        fileType: messageText.includes('.pdf') ? 'pdf' : null
      };
      console.log('🛡️ [DEBUG] Step 2: Metadata created:', metadata);

      console.log('🛡️ [DEBUG] Step 3: Calling cloudAnalyzer.analyze...');
      const cloudResult = await cloudAnalyzer.analyze(messageText, metadata);
      console.log('🛡️ [DEBUG] Step 4: cloudResult received:', cloudResult);
      
      // VPS Agent verdict is the ONLY authority - no local override
      const analysis = {
        riskScore: cloudResult.risk_score,
        isScam: cloudResult.risk_level === 'critical',
        isSuspicious: cloudResult.risk_level === 'caution',
        riskLevel: cloudResult.risk_level,
        explanation: cloudResult.explanation,
        categories: [],
        recommendations: [],
        matchedPatterns: [],
        source: 'vps-agent'
      };

      console.log('🛡️ [DEBUG] Step 5: Analysis object:', analysis);
      console.log('🛡️ [DEBUG] isScam:', analysis.isScam, 'isSuspicious:', analysis.isSuspicious);
      
      handleAnalysisResult(messageElement, messageText, analysis);
    } catch (error) {
      console.error('🛡️ VPS Agent unavailable:', error);
      console.error('🛡️ Error name:', error.name);
      console.error('🛡️ Error message:', error.message);
      console.error('🛡️ Error stack:', error.stack);
      // Show error badge instead of falling back to local detection
      showErrorBadge(messageElement, 'Agent unavailable - check connection');
    }
  }

  /**
   * Show error badge when VPS Agent is unavailable
   */
  function showErrorBadge(messageElement, errorMessage) {
    const badge = document.createElement('div');
    badge.className = 'scamshield-badge shield-badge';
    
    const badgeInner = document.createElement('div');
    badgeInner.style.cssText = `
      background: #9ca3af;
      color: white;
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      margin-bottom: 8px;
      display: inline-block;
      z-index: 9999;
    `;
    badgeInner.title = errorMessage;
    badgeInner.textContent = `🛡️ ${errorMessage}`;
    badge.appendChild(badgeInner);
    
    messageElement.style.position = 'relative';
    messageElement.prepend(badge);
  }

  /**
   * Handle the combined analysis result and update UI
   */
  function handleAnalysisResult(messageElement, messageText, analysis) {
    console.log('🛡️ [DEBUG] handleAnalysisResult called with:', {
      isScam: analysis.isScam,
      isSuspicious: analysis.isSuspicious,
      riskLevel: analysis.riskLevel,
      riskScore: analysis.riskScore
    });
    
    // If suspicious or scam, add badge
    if (analysis.isScam || analysis.isSuspicious) {
      // CRITICAL: Double-check for existing badge before adding
      if (messageElement.querySelector('.scamshield-badge')) {
        console.log('🛡️ Badge already exists, skipping duplicate');
        return;
      }
      
      console.log(`🚨 UniversalShield ALERT [${analysis.source || 'local'}]:`, 
                  analysis.riskLevel.toUpperCase(), 
                  `(${analysis.riskScore}%)`, messageText.substring(0, 100));

      const badge = createBadge(analysis);
      const tooltip = createTooltip(analysis);
      
      // Create backdrop for centered modal
      const backdrop = document.createElement('div');
      backdrop.className = 'scamshield-tooltip-backdrop';
      
      // Add badge to message
      messageElement.style.position = 'relative';
      messageElement.prepend(badge);
      document.body.appendChild(backdrop);
      document.body.appendChild(tooltip);

      // Show tooltip on badge click (always open, close others)
      badge.addEventListener('click', (e) => {
        e.stopPropagation();
        
        // Close all other tooltips and backdrops
        document.querySelectorAll('.scamshield-tooltip-visible').forEach(t => {
          t.classList.remove('scamshield-tooltip-visible');
        });
        document.querySelectorAll('.scamshield-tooltip-backdrop.visible').forEach(b => {
          b.classList.remove('visible');
        });
        
        // Open this tooltip with backdrop
        backdrop.classList.add('visible');
        tooltip.classList.add('scamshield-tooltip-visible');
      });

      // Handle close button
      tooltip.querySelector('.scamshield-close-btn')?.addEventListener('click', (e) => {
        e.stopPropagation();
        tooltip.classList.remove('scamshield-tooltip-visible');
        backdrop.classList.remove('visible');
      });
      
      // Close on backdrop click
      backdrop.addEventListener('click', () => {
        tooltip.classList.remove('scamshield-tooltip-visible');
        backdrop.classList.remove('visible');
      });

      // Handle report button
      tooltip.querySelector('.scamshield-report-btn')?.addEventListener('click', () => {
        reportScam(messageText, analysis, false);
        badge.remove();
        tooltip.remove();
        backdrop.remove();
      });

      // Handle false positive button
      tooltip.querySelector('.scamshield-dismiss-btn')?.addEventListener('click', () => {
        reportScam(messageText, analysis, true);
        badge.remove();
        tooltip.remove();
        backdrop.remove();
      });

      // Update stats
      if (analysis.isScam) {
        stats.scamsBlocked++;
      } else {
        stats.suspiciousFound++;
      }

      // Highlight message
      messageElement.style.border = analysis.isScam ? "2px solid #ff0000" : "2px solid #ffcc00";
      messageElement.style.borderRadius = "8px";
      messageElement.style.padding = "12px";
      messageElement.style.backgroundColor = analysis.isScam ? "rgba(255, 0, 0, 0.05)" : "rgba(255, 204, 0, 0.05)";
    }

    // Save stats
    chrome.storage.local.set({ scamshield_stats: stats });
  }

  /**
   * Report a scam (sends to background script and VPS Agent)
   */
  async function reportScam(messageText, analysis, isFalsePositive = false) {
    // Extract features for ML training
    const metadata = {
      platform: 'linkedin',
      accountAge: 365,
      connectionDegree: 3,
      hasAttachment: messageText.includes('Download') || messageText.includes('.pdf'),
      fileType: messageText.includes('.pdf') ? 'pdf' : null
    };
    
    let features = {};
    if (typeof FeatureExtractor !== 'undefined') {
      features = new FeatureExtractor().extract(messageText, metadata);
    }

    const reportData = {
      type: 'REPORT_SCAM',
      data: {
        messageText: messageText.substring(0, 500),
        analysis: analysis,
        features: features,
        isFalsePositive: isFalsePositive,
        url: window.location.href,
        timestamp: new Date().toISOString()
      }
    };

    // 1. Notify background script
    chrome.runtime.sendMessage(reportData);

    // 2. Send to VPS Agent for ML growth
    try {
      const apiUrl = 'https://jobguard.nomadahealth.com';
      const response = await fetch(`${apiUrl}/api/v1/report-scam`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-License-Key': licenseKey || ''
        },
        body: JSON.stringify({
          features: features,
          is_scam: !isFalsePositive,
          predicted_risk_score: analysis.riskScore,
          predicted_risk_level: analysis.riskLevel || 'unknown',
          platform: 'linkedin'
        })
      });
      const result = await response.json();
      console.log('🛡️ VPS Agent response:', result);
    } catch (error) {
      console.error('🛡️ Failed to send feedback to VPS Agent:', error);
    }

    console.log('🛡️ Feedback sent:', isFalsePositive ? 'marked as safe' : 'reported as scam');
  }

  /**
   * Scan all messages on page
   */
  function scanAllMessages() {
    console.log('🛡️ UniversalShield: Scanning page for messages...');
    console.log('🛡️ CloudAnalyzer initialized:', cloudAnalyzer !== null);
    
    let totalScanned = 0;
    MESSAGE_SELECTORS.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      console.log(`🛡️ Selector "${selector}" found ${elements.length} elements`);
      if (elements.length > 0) {
        elements.forEach(scanMessage);
        totalScanned += elements.length;
      }
    });
    
    console.log(`🛡️ UniversalShield: Scanned ${totalScanned} message elements`);
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
    
    // Close tooltips when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.scamshield-badge') && !e.target.closest('.scamshield-tooltip')) {
        document.querySelectorAll('.scamshield-tooltip-visible').forEach(tooltip => {
          tooltip.classList.remove('scamshield-tooltip-visible');
        });
      }
    });
    
    // Initial scan
    setTimeout(scanAllMessages, 1000);
    
    // Set up observer for new messages
    setupObserver();
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  } catch (error) {
    console.error('🛡️ FATAL ERROR in UniversalShield:', error);
    console.error('🛡️ Stack trace:', error.stack);
  }
})();
