/**
 * UniversalShield - Background Service Worker
 */

// Initialize stats on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('🛡️ UniversalShield installed');
  
  chrome.storage.local.set({
    scamshield_stats: {
      scansToday: 0,
      scamsBlocked: 0,
      suspiciousFound: 0,
      totalScans: 0,
      totalScamsBlocked: 0,
      installDate: new Date().toISOString()
    },
    scamshield_reports: [],
    scamshield_settings: {
      enabled: true,
      showBadges: true,
      autoScan: true,
      notifyOnScam: true
    }
  });
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'REPORT_SCAM') {
    handleScamReport(message.data);
    sendResponse({ success: true });
  }
  
  if (message.type === 'GET_STATS') {
    chrome.storage.local.get(['scamshield_stats'], (result) => {
      sendResponse(result.scamshield_stats || {});
    });
    return true;
  }
  
  if (message.type === 'GET_SETTINGS') {
    chrome.storage.local.get(['scamshield_settings'], (result) => {
      sendResponse(result.scamshield_settings || {});
    });
    return true;
  }
  
  if (message.type === 'UPDATE_SETTINGS') {
    chrome.storage.local.set({ scamshield_settings: message.data });
    sendResponse({ success: true });
  }
  
  // API call from content script - bypasses LinkedIn's CSP
  if (message.type === 'API_CALL') {
    handleApiCall(message.url, message.options)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
});

/**
 * Handle API calls from content script (bypasses page CSP)
 */
async function handleApiCall(url, options) {
  console.log('🛡️ [BG] API call to:', url);
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return await response.json();
}

/**
 * Handle scam report from user
 */
function handleScamReport(data) {
  chrome.storage.local.get(['scamshield_reports'], (result) => {
    const reports = result.scamshield_reports || [];
    
    reports.unshift({
      ...data,
      id: Date.now().toString()
    });
    
    if (reports.length > 100) {
      reports.pop();
    }
    
    chrome.storage.local.set({ scamshield_reports: reports });
    
    chrome.storage.local.get(['scamshield_stats'], (statsResult) => {
      const stats = statsResult.scamshield_stats || {};
      stats.totalScamsBlocked = (stats.totalScamsBlocked || 0) + 1;
      chrome.storage.local.set({ scamshield_stats: stats });
    });
  });
  
  console.log('🛡️ Scam reported:', data.analysis.riskLevel, data.analysis.riskScore);
}
