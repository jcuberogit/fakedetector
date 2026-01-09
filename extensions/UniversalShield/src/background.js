/**
 * LinkedIn ScamShield - Background Service Worker
 * 100% Open Source - MIT License
 */

// Initialize stats on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('🛡️ LinkedIn ScamShield installed');
  
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
    return true; // Keep channel open for async response
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
});

/**
 * Handle scam report from user
 */
function handleScamReport(data) {
  chrome.storage.local.get(['scamshield_reports'], (result) => {
    const reports = result.scamshield_reports || [];
    
    // Add new report (limit to last 100)
    reports.unshift({
      ...data,
      id: Date.now().toString()
    });
    
    if (reports.length > 100) {
      reports.pop();
    }
    
    chrome.storage.local.set({ scamshield_reports: reports });
    
    // Update total blocked count
    chrome.storage.local.get(['scamshield_stats'], (statsResult) => {
      const stats = statsResult.scamshield_stats || {};
      stats.totalScamsBlocked = (stats.totalScamsBlocked || 0) + 1;
      chrome.storage.local.set({ scamshield_stats: stats });
    });
  });
  
  console.log('🛡️ Scam reported:', data.analysis.riskLevel, data.analysis.riskScore);
}

// Reset daily stats at midnight
chrome.alarms.create('resetDailyStats', {
  when: getNextMidnight(),
  periodInMinutes: 24 * 60
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'resetDailyStats') {
    chrome.storage.local.get(['scamshield_stats'], (result) => {
      const stats = result.scamshield_stats || {};
      
      // Accumulate to totals before reset
      stats.totalScans = (stats.totalScans || 0) + (stats.scansToday || 0);
      stats.totalScamsBlocked = (stats.totalScamsBlocked || 0) + (stats.scamsBlocked || 0);
      
      // Reset daily counters
      stats.scansToday = 0;
      stats.scamsBlocked = 0;
      stats.suspiciousFound = 0;
      
      chrome.storage.local.set({ scamshield_stats: stats });
    });
  }
});

/**
 * Get timestamp for next midnight
 */
function getNextMidnight() {
  const now = new Date();
  const midnight = new Date(now);
  midnight.setHours(24, 0, 0, 0);
  return midnight.getTime();
}
