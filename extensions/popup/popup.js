/**
 * UniversalShield - Popup Script
 */

document.addEventListener('DOMContentLoaded', () => {
  loadStats();
  loadSettings();
  loadLicenseStatus();
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

  // Upgrade button
  const upgradeBtn = document.getElementById('upgradeBtn');
  if (upgradeBtn) {
    upgradeBtn.addEventListener('click', () => {
      chrome.tabs.create({ url: 'https://universalshield.dev/upgrade' });
    });
    
    // Right-click to show license input
    upgradeBtn.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      document.getElementById('licenseInput').style.display = 'block';
    });
  }

  // Activate license button
  const activateBtn = document.getElementById('activateBtn');
  if (activateBtn) {
    activateBtn.addEventListener('click', async () => {
      const key = document.getElementById('licenseKey').value.trim();
      if (key) {
        await saveLicense(key);
        location.reload();
      }
    });
  }
}

function updateSetting(key, value) {
  chrome.storage.local.get(['scamshield_settings'], (result) => {
    const settings = result.scamshield_settings || {};
    settings[key] = value;
    chrome.storage.local.set({ scamshield_settings: settings });
  });
}

async function loadLicenseStatus() {
  const license = await checkLicense();
  
  const tierBadge = document.getElementById('tierBadge');
  const tierInfo = document.getElementById('tierInfo');
  const upgradeSection = document.getElementById('upgradeSection');
  const scansRemaining = document.getElementById('scansRemaining');
  
  if (license.valid && license.tier === 'pro') {
    // Pro tier
    tierBadge.textContent = '⭐ Pro Active';
    tierBadge.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    tierBadge.style.color = 'white';
    tierInfo.innerHTML = '<span style="color: #667eea; font-weight: 600;">✅ Unlimited scans • All features enabled</span>';
    upgradeSection.style.display = 'none';
  } else {
    // Free tier
    tierBadge.textContent = 'Free Tier';
    tierBadge.style.background = '#f5f5f5';
    tierBadge.style.color = '#666';
    
    const remaining = license.scans_remaining || 50;
    scansRemaining.textContent = `${remaining} scans remaining today`;
    
    if (remaining < 10) {
      scansRemaining.style.color = '#f44336';
    }
    
    upgradeSection.style.display = 'block';
  }
}

async function checkLicense() {
  const stored = await chrome.storage.sync.get(['scamshield_license']);
  
  if (!stored.scamshield_license) {
    return { valid: false, tier: 'free', scans_remaining: 50 };
  }
  
  try {
    const response = await fetch('https://api.tucan.store/api/v1/subscription/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ license_key: stored.scamshield_license })
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('License validation error:', error);
    return { valid: false, tier: 'free', scans_remaining: 50 };
  }
}

async function saveLicense(licenseKey) {
  await chrome.storage.sync.set({ scamshield_license: licenseKey });
  await chrome.storage.local.set({ license_last_check: Date.now() });
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
