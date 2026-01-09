/**
 * LinkedIn ScamShield - Popup Script
 * 100% Open Source - MIT License
 */

document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadSettings();
  setupEventListeners();
});

function loadStats() {
  chrome.storage.local.get(['scamshield_stats'], (result) => {
    const stats = result.scamshield_stats || {};
    document.getElementById('scamsBlocked').textContent = stats.scamsBlocked || 0;
    document.getElementById('suspiciousFound').textContent = stats.suspiciousFound || 0;
    document.getElementById('scansToday').textContent = stats.scansToday || 0;
  });
}

function loadSettings() {
  chrome.storage.local.get(['scamshield_settings'], (result) => {
    const settings = result.scamshield_settings || { enabled: true, showBadges: true };
    document.getElementById('enableScanning').checked = settings.enabled;
    document.getElementById('showBadges').checked = settings.showBadges;
    updateStatusIndicator(settings.enabled);
  });
}

function setupEventListeners() {
  document.getElementById('enableScanning').addEventListener('change', (e) => {
    updateSetting('enabled', e.target.checked);
    updateStatusIndicator(e.target.checked);
  });

  document.getElementById('showBadges').addEventListener('change', (e) => {
    updateSetting('showBadges', e.target.checked);
  });
}

function updateSetting(key, value) {
  chrome.storage.local.get(['scamshield_settings'], (result) => {
    const settings = result.scamshield_settings || {};
    settings[key] = value;
    chrome.storage.local.set({ scamshield_settings: settings });
  });
}

function updateStatusIndicator(enabled) {
  const statusDot = document.querySelector('.status-dot');
  const statusText = document.querySelector('.status-text');
  const status = document.querySelector('.status');
  
  if (enabled) {
    statusDot.classList.add('active');
    statusText.textContent = 'Active';
    status.style.background = '#e8f5e9';
    statusDot.style.background = '#4caf50';
    statusText.style.color = '#2e7d32';
  } else {
    statusDot.classList.remove('active');
    statusText.textContent = 'Paused';
    status.style.background = '#fff3e0';
    statusDot.style.background = '#ff9800';
    statusText.style.color = '#e65100';
  }
}
