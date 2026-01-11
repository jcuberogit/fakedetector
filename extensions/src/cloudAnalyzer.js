console.log('🛡️ cloudAnalyzer.js loading...');

/**
 * Cloud Analyzer - PRO Tier
 * Enhanced ML analysis with anonymized features only
 * Privacy guarantee: NEVER sends raw message content
 */

class FeatureExtractor {
  constructor() {
    this.urgencyKeywords = [
      'urgent', 'immediately', 'now', 'today', 'asap', 'hurry',
      'limited time', 'expires', 'act now', 'don\'t miss'
    ];
    
    this.moneyKeywords = [
      'money', 'cash', 'payment', 'bank', 'account', 'wire',
      'transfer', 'deposit', 'bitcoin', 'crypto', 'investment',
      'profit', 'earn', 'income', 'fee', 'prize', 'lottery'
    ];
    
    this.credentialKeywords = [
      'password', 'login', 'verify', 'confirm', 'account',
      'username', 'credentials', 'security', 'suspended'
    ];
    
    // Rachel Good pattern keywords
    this.recruiterKeywords = [
      'recruiter', 'hiring', 'opportunity', 'position', 'resume',
      'cv', 'application', 'interview', 'job opening', 'career'
    ];
    
    // Financial phishing keywords
    this.financialPhishingKeywords = [
      'destiny', 'mastercard', 'credit card', 'credit limit',
      'security deposit', 'pre-approved', 'congratulations',
      'qualify', 'approval', 'financial opportunity'
    ];
    
    // CV SCAM indicators (offers to improve CV for fee)
    this.cvScamKeywords = [
      'improve your cv', 'improve your resume', 'review your cv', 'review your resume',
      'optimize your cv', 'optimize your resume', 'enhance your profile',
      'help with your cv', 'rewrite your resume', 'cv services', 'resume services',
      'your resume shows', 'your cv shows', 'reshape it', 'restructure your',
      'ats systems', 'ats system', 'applicant tracking', 'frameworks like',
      'star method', 'car method', 'holding you back', 'not getting noticed',
      'honest recommendations', 'better shot at', 'make it past screening'
    ];
    
    // LEGITIMATE job offer indicators
    this.legitimateJobKeywords = [
      'job description', 'job opening', 'position available', 'we are hiring',
      'job requirements', 'qualifications', 'responsibilities', 'years experience',
      'send your cv', 'send your resume', 'submit your cv', 'apply for',
      'job posting', 'vacancy', 'employment opportunity'
    ];
    
    // Technical skills (indicates real job)
    this.technicalSkillsKeywords = [
      'java', 'python', 'javascript', 'react', 'angular', 'node', 'sql',
      'aws', 'azure', 'docker', 'kubernetes', 'agile', 'scrum',
      'developer', 'engineer', 'architect', 'analyst', 'manager',
      'adobe', 'sap', 'hybris', 'aem', 'salesforce', 'oracle'
    ];
    
    // Legitimate transactional/automated emails
    this.transactionalKeywords = [
      'we received your application', 'thank you for applying',
      'application received', 'thank you for your interest',
      'order confirmation', 'shipping confirmation', 'delivery update',
      'password reset', 'verify your email', 'welcome to',
      'subscription confirmed', 'unsubscribe', 'do not reply',
      'automated message', 'noreply', 'no-reply'
    ];
    
    // NLP scam indicators - common scam phrases
    this.scamPhraseIndicators = [
      'i saw your profile and i am very impressed',
      'fits your profile perfectly',
      'quick call or can you share your resume',
      'remote position paying',
      'per hour working from home',
      'guaranteed interviews',
      'guarantee you will get',
      'our fee is very affordable',
      'small investment required',
      'pay a small fee',
      'processing fee',
      'registration fee'
    ];
    
    // Fee-based scam indicators
    this.feeBasedScamKeywords = [
      'our fee', 'small fee', 'affordable fee', 'one-time fee',
      'registration fee', 'processing fee', 'guarantee interviews',
      'guaranteed job', 'guaranteed placement', 'pay to',
      'investment required', 'upfront payment', 'advance payment'
    ];
    
    // Exclusion patterns - legitimate automated messages
    this.legitimateAutomatedPatterns = [
      'move forward with other candidates',
      'we have decided to pursue other candidates',
      'thank you for your interest in',
      'we appreciate your application',
      'position has been filled',
      'not moving forward with your application'
    ];
    
    // ============ CIALDINI PSYCHOLOGICAL ATTACK VECTORS ============
    
    // Authority Heuristic - False credentialing, Big Tech names to lower defenses
    this.authorityPatterns = [
      'recruiter from google', 'recruiter from meta', 'recruiter from amazon',
      'recruiter from microsoft', 'recruiter from apple', 'recruiter from ebay',
      'fortune 500', 'senior vp of', 'vice president of', 'director of talent',
      'global talent', 'head of recruitment', 'chief people officer',
      'we saw your profile at the', 'global summit', 'exclusive opportunity'
    ];
    
    // Scarcity & Urgency - Artificial deadlines, pressure tactics
    this.scarcityPatterns = [
      'urgent requirement', 'immediate start', 'only 2 spots left',
      'only 3 spots', 'last vacancy', 'reply within 24 hours',
      'closing the portal', 'deadline tomorrow', 'limited positions',
      'act now', 'don\'t miss this', 'expires today', 'final call',
      'bonus for immediate response', 'secure your spot'
    ];
    
    // Liking & Flattery - Love bombing, excessive praise
    this.flatteryPatterns = [
      'most impressive profile', 'perfect fit for', 'exactly what we need',
      'visionary like you', 'your background is exceptional', 'standout candidate',
      'top talent', 'highly qualified', 'impressed by your experience',
      'you are the ideal candidate', 'perfect match for our team'
    ];
    
    // Reciprocity Trap - Free offers to create obligation
    this.reciprocityPatterns = [
      'free resume audit', 'free cv review', 'free consultation',
      'i will give you', 'share a list of internal jobs',
      'give me your personal whatsapp', 'free tool', 'complimentary review',
      'at no cost to you', 'free assessment', 'free career advice'
    ];
    
    // Cognitive Ease - Easy money, too good to be true
    this.cognitiveEasePatterns = [
      'no interview needed', 'just a quick chat', 'high salary for',
      'hours of work per day', 'simple tasks', 'high rewards',
      'easy money', 'work from home', 'flexible hours',
      '$50 per hour', '$100 per hour', 'per hour remote',
      'minimal effort', 'passive income', 'side hustle'
    ];
    
    // Social Proof - Fake consensus, tribalism
    this.socialProofPatterns = [
      'other candidates have already', 'many professionals joined',
      'architects from', 'developers from', 'engineers from',
      'as a fellow', 'fellow mba', 'fellow graduate',
      'people like you', 'professionals in your field'
    ];
    
    // ============ CISA SOCIAL ENGINEERING TACTICS ============
    
    // Pretexting - Fabricated scenarios
    this.pretextingPatterns = [
      'confidential audit', 'security verification', 'account update required',
      'urgent system update', 'verify your identity', 'confirm your details',
      'data breach notification', 'suspicious activity detected'
    ];
    
    // Quid Pro Quo - Exchange scams
    this.quidProQuoPatterns = [
      'salary range if you', 'give me your ssn', 'need your id',
      'bank details for', 'personal information for', 'share your credentials',
      'access in exchange for', 'information in return'
    ];
    
    // WhatsApp/Telegram redirection
    this.redirectionPatterns = [
      'contact me on whatsapp', 'reach me on telegram', 'text me at',
      'call me on my personal', 'continue on whatsapp', 'move to telegram',
      'personal number is', 'add me on'
    ];
    
    // ============ APWG MALICIOUS INDICATORS ============
    
    // High-alert NLP phrases
    this.highAlertPhrases = [
      'kindly', 'do the needful', 'verify your identity',
      'locked account', 'suspended account', 'job offer without interview',
      'investment opportunity', 'crypto payroll', 'bitcoin salary',
      'action required immediately', 'confirm now'
    ];
  }
  
  extract(message, metadata) {
    const messageLower = message.toLowerCase();
    
    // Returns ONLY numerical features - NEVER raw text
    return {
      // Message structure
      message_length: message.length,
      word_count: message.split(/\s+/).length,
      sentence_count: message.split(/[.!?]+/).length,
      avg_word_length: this.calculateAvgWordLength(message),
      
      // Keyword density
      urgency_keywords_count: this.countKeywords(messageLower, this.urgencyKeywords),
      money_keywords_count: this.countKeywords(messageLower, this.moneyKeywords),
      credential_keywords_count: this.countKeywords(messageLower, this.credentialKeywords),
      
      // Rachel Good pattern features
      recruiter_keywords_count: this.countKeywords(messageLower, this.recruiterKeywords),
      location_inquiry: /where are you located|what.?s your location|where do you live/.test(messageLower) ? 1 : 0,
      experience_inquiry: /how many years|years of experience|your experience/.test(messageLower) ? 1 : 0,
      // Gmail in message - detect @gmail.com email addresses IN the message text
      gmail_in_message: this.detectGmailInMessage(messageLower) ? 1 : 0,
      gmail_recruiter_combo: (this.detectGmailInMessage(messageLower) && this.countKeywords(messageLower, this.recruiterKeywords) > 0) ? 1 : 0,
      vague_address_pattern: /\d+\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr)(?!\s+\w)/i.test(message) ? 1 : 0,
      
      // NLP scam phrase indicators
      scam_phrase_count: this.countKeywords(messageLower, this.scamPhraseIndicators),
      fee_based_scam_count: this.countKeywords(messageLower, this.feeBasedScamKeywords),
      
      // Legitimate automated message detection (exclusion)
      is_legitimate_rejection: this.countKeywords(messageLower, this.legitimateAutomatedPatterns) > 0 ? 1 : 0,
      
      // ============ CIALDINI PSYCHOLOGICAL VECTORS ============
      authority_score: this.countKeywords(messageLower, this.authorityPatterns),
      scarcity_score: this.countKeywords(messageLower, this.scarcityPatterns),
      flattery_score: this.countKeywords(messageLower, this.flatteryPatterns),
      reciprocity_score: this.countKeywords(messageLower, this.reciprocityPatterns),
      cognitive_ease_score: this.countKeywords(messageLower, this.cognitiveEasePatterns),
      social_proof_score: this.countKeywords(messageLower, this.socialProofPatterns),
      
      // ============ CISA SOCIAL ENGINEERING ============
      pretexting_score: this.countKeywords(messageLower, this.pretextingPatterns),
      quid_pro_quo_score: this.countKeywords(messageLower, this.quidProQuoPatterns),
      redirection_score: this.countKeywords(messageLower, this.redirectionPatterns),
      
      // ============ APWG MALICIOUS INDICATORS ============
      high_alert_score: this.countKeywords(messageLower, this.highAlertPhrases),
      
      // Combined psychological attack score (Cialdini layers)
      psych_attack_total: this.calculatePsychAttackScore(messageLower),
      
      // Financial phishing features
      financial_phishing_keywords_count: this.countKeywords(messageLower, this.financialPhishingKeywords),
      credit_card_mention: /credit card|mastercard|visa|amex/.test(messageLower) ? 1 : 0,
      credit_limit_mention: /credit limit|\$\d+\s*credit/.test(messageLower) ? 1 : 0,
      security_deposit_mention: /security deposit|deposit required/.test(messageLower) ? 1 : 0,
      
      // CV scam vs legitimate job detection
      cv_scam_keywords_count: this.countKeywords(messageLower, this.cvScamKeywords),
      legitimate_job_keywords_count: this.countKeywords(messageLower, this.legitimateJobKeywords),
      technical_skills_count: this.countKeywords(messageLower, this.technicalSkillsKeywords),
      has_corporate_email: this.hasCorporateEmail(metadata) ? 1 : 0,
      has_specific_job_title: this.hasJobTitle(messageLower) ? 1 : 0,
      
      // Transactional/automated email detection
      transactional_keywords_count: this.countKeywords(messageLower, this.transactionalKeywords),
      is_transactional_email: this.isTransactionalEmail(messageLower) ? 1 : 0,
      
      // Links and attachments
      link_count: (message.match(/https?:\/\//g) || []).length,
      has_shortened_url: this.hasShortenedUrl(message) ? 1 : 0,
      file_attachment: metadata.hasAttachment ? 1 : 0,
      file_extension_risk: this.getExtensionRisk(metadata.fileType),
      
      // Linguistic features
      exclamation_count: (message.match(/!/g) || []).length,
      question_count: (message.match(/\?/g) || []).length,
      caps_ratio: this.calculateCapsRatio(message),
      number_count: (message.match(/\d+/g) || []).length,
      currency_symbol_count: (message.match(/[$€£]/g) || []).length,
      
      // Social context (anonymized)
      sender_account_age_days: metadata.accountAge || 0,
      connection_degree: metadata.connectionDegree || 3,
      previous_interactions: Math.min(metadata.previousInteractions || 0, 100),
      
      // Platform and context (categorical IDs)
      platform_id: this.platformToId(metadata.platform),
      context_type_id: this.contextToId(metadata.claimedRole),
      
      // Behavioral flags (binary)
      requests_download: this.requestsDownload(messageLower) ? 1 : 0,
      requests_payment: this.requestsPayment(messageLower) ? 1 : 0,
      requests_credentials: this.requestsCredentials(messageLower) ? 1 : 0,
      has_urgency: this.countKeywords(messageLower, this.urgencyKeywords) > 0 ? 1 : 0
    };
  }
  
  calculateAvgWordLength(message) {
    const words = message.split(/\s+/).filter(w => w.length > 0);
    if (words.length === 0) return 0;
    return words.reduce((sum, word) => sum + word.length, 0) / words.length;
  }
  
  countKeywords(text, keywords) {
    let count = 0;
    for (const keyword of keywords) {
      if (text.includes(keyword)) count++;
    }
    return count;
  }
  
  hasShortenedUrl(message) {
    const shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly', 'adf.ly'];
    return shorteners.some(s => message.toLowerCase().includes(s));
  }
  
  extractUrls(message) {
    // Extract all URLs from message for threat intelligence verification
    const urlPattern = /https?:\/\/[^\s<>"{}|\\^`\[\]]+/gi;
    const urls = message.match(urlPattern) || [];
    
    // Also extract URL shorteners
    const shortenerPatterns = [
      /bit\.ly\/\S+/gi, /tinyurl\.com\/\S+/gi, /goo\.gl\/\S+/gi,
      /t\.co\/\S+/gi, /ow\.ly\/\S+/gi, /is\.gd\/\S+/gi
    ];
    
    shortenerPatterns.forEach(pattern => {
      const matches = message.match(pattern) || [];
      matches.forEach(m => {
        if (!m.startsWith('http')) {
          urls.push('https://' + m);
        }
      });
    });
    
    return [...new Set(urls)]; // Remove duplicates
  }
  
  extractEmailDomains(message) {
    // Extract email domains for verification
    const emailPattern = /[\w.-]+@([\w.-]+\.\w+)/gi;
    const domains = [];
    let match;
    while ((match = emailPattern.exec(message)) !== null) {
      domains.push(match[1].toLowerCase());
    }
    return [...new Set(domains)];
  }
  
  getExtensionRisk(fileType) {
    if (!fileType) return 0.0;
    
    const dangerous = ['exe', 'bat', 'cmd', 'scr', 'vbs', 'js', 'jar', 'msi'];
    const safe = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'png'];
    
    const ext = fileType.toLowerCase();
    if (dangerous.includes(ext)) return 1.0;
    if (safe.includes(ext)) return 0.1;
    return 0.5;
  }
  
  calculateCapsRatio(message) {
    const letters = message.match(/[a-zA-Z]/g) || [];
    if (letters.length === 0) return 0;
    const caps = message.match(/[A-Z]/g) || [];
    return caps.length / letters.length;
  }
  
  platformToId(platform) {
    const map = { linkedin: 1, gmail: 2, outlook: 3 };
    return map[platform] || 0;
  }
  
  contextToId(context) {
    const map = {
      recruiter: 1, investor: 2, friend: 3, coworker: 4,
      support: 5, delivery_service: 6, professional: 7
    };
    return map[context] || 0;
  }
  
  requestsDownload(message) {
    return /download|install|run|execute|open file/.test(message);
  }
  
  requestsPayment(message) {
    return /send money|wire|transfer|pay|deposit|bank details/.test(message);
  }
  
  requestsCredentials(message) {
    return this.countKeywords(message, this.credentialKeywords) >= 2;
  }
  
  detectGmailInMessage(message) {
    // Detect @gmail.com email addresses mentioned IN the message text
    // Pattern: something@gmail.com (recruiter scam pattern)
    return /@gmail\.com/i.test(message);
  }
  
  calculatePsychAttackScore(message) {
    // Layer analysis per Cialdini framework
    // If 3+ psychological triggers present, risk increases significantly
    let triggers = 0;
    
    if (this.countKeywords(message, this.authorityPatterns) > 0) triggers++;
    if (this.countKeywords(message, this.scarcityPatterns) > 0) triggers++;
    if (this.countKeywords(message, this.flatteryPatterns) > 0) triggers++;
    if (this.countKeywords(message, this.reciprocityPatterns) > 0) triggers++;
    if (this.countKeywords(message, this.cognitiveEasePatterns) > 0) triggers++;
    if (this.countKeywords(message, this.socialProofPatterns) > 0) triggers++;
    if (this.countKeywords(message, this.pretextingPatterns) > 0) triggers++;
    if (this.countKeywords(message, this.quidProQuoPatterns) > 0) triggers++;
    if (this.countKeywords(message, this.redirectionPatterns) > 0) triggers++;
    if (this.countKeywords(message, this.highAlertPhrases) > 0) triggers++;
    
    return triggers;  // 0-10 scale, 3+ = high risk
  }
  
  hasCorporateEmail(metadata) {
    const email = (metadata.senderEmail || '').toLowerCase();
    if (!email) return false;
    
    const freeEmailDomains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 
                              'aol.com', 'mail.com', 'protonmail.com', 'icloud.com'];
    
    for (const domain of freeEmailDomains) {
      if (email.includes(domain)) return false;
    }
    
    return email.includes('@');
  }
  
  hasJobTitle(message) {
    const jobTitles = [
      'developer', 'engineer', 'architect', 'analyst', 'manager',
      'director', 'specialist', 'consultant', 'administrator',
      'coordinator', 'lead', 'senior', 'junior', 'intern'
    ];
    return jobTitles.some(title => message.includes(title));
  }
  
  isTransactionalEmail(message) {
    // Detect legitimate transactional/automated emails
    const transactionalPatterns = [
      /we received your application/i,
      /thank you for (applying|your interest|your application)/i,
      /application (received|submitted|confirmed)/i,
      /order (confirmation|confirmed|shipped)/i,
      /(password|account) (reset|recovery)/i,
      /verify your (email|account)/i,
      /welcome to/i,
      /(do not|don't) reply/i,
      /this is an automated/i,
      /noreply|no-reply/i,
      /unsubscribe/i,
      /bamboohr|workday|greenhouse|lever|icims/i  // ATS systems
    ];
    return transactionalPatterns.some(pattern => pattern.test(message));
  }
}

class CloudAnalyzer {
  constructor(apiUrl, licenseKey) {
    this.apiUrl = apiUrl || 'https://jobguard.nomadahealth.com';
    this.licenseKey = licenseKey;
    this.featureExtractor = new FeatureExtractor();
  }
  
  async analyze(message, metadata) {
    // ============ LAYERED VERIFICATION (Cost Optimization) ============
    // Layer 1: FREE - PhishTank/Google Safe Browsing (URL blacklist)
    // Layer 2: FREE - Local NLP patterns (Cialdini, CISA)
    // Layer 3: PAID - AI analysis only if needed
    
    console.log('🛡️ [ANALYZE] Starting layered verification...');
    
    // Step 0: Extract URLs for FREE threat intel check
    const urls = this.featureExtractor.extractUrls(message);
    if (urls.length > 0) {
      console.log('🛡️ [LAYER 1] Found URLs, checking threat intel:', urls);
      const urlResult = await this.verifyUrls(urls);
      if (urlResult && urlResult.has_threats) {
        console.log('🛡️ [LAYER 1] MALICIOUS URL DETECTED!', urlResult);
        return {
          risk_score: 100,
          risk_level: 'critical',
          explanation: '🚨 MALICIOUS URL DETECTED: URL found in PhishTank/Google Safe Browsing blacklist. Do NOT click any links in this message.',
          source: 'threat_intel',
          tier: 'free',
          threat_details: urlResult.results
        };
      }
    }
    
    // Step 1: Extract anonymized features LOCALLY (FREE)
    console.log('🛡️ [LAYER 2] Local NLP analysis...');
    const features = this.featureExtractor.extract(message, metadata);
    console.log('🛡️ [ANALYZE] Features extracted:', JSON.stringify(features));
    console.log('🛡️ [ANALYZE] CV scam count:', features.cv_scam_keywords_count);
    console.log('🛡️ [ANALYZE] Psych attack total:', features.psych_attack_total);
    
    // Step 2: Send ONLY features to API with retry logic
    const maxRetries = 2;
    let lastError;
    const fullUrl = `${this.apiUrl}/api/v1/analyze-features`;
    console.log('🛡️ [API] Calling URL:', fullUrl);
    console.log('🛡️ [API] With features:', JSON.stringify(features));
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        // Use background script to bypass LinkedIn's CSP
        const result = await this.apiCallViaBackground(fullUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-License-Key': this.licenseKey || ''
          },
          body: JSON.stringify({ features })
        });
        
        console.log('🛡️ [ANALYZE] API Response:', JSON.stringify(result));
        console.log('🛡️ [ANALYZE] Risk score:', result.risk_score, 'Risk level:', result.risk_level);
        
        return {
          risk_score: result.risk_score,
          risk_level: result.risk_level,
          explanation: result.explanation,
          source: 'cloud',
          tier: result.tier,
          scans_remaining: result.scans_remaining
        };
      } catch (error) {
        lastError = error;
        console.warn(`Cloud analysis attempt ${attempt + 1} failed:`, error.message);
        
        // Don't retry on 4xx errors (client errors) including 429
        if (error.message.includes('40') || error.message.includes('429')) {
          break;
        }
        
        // Wait before retry (exponential backoff)
        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt)));
        }
      }
    }
    
    console.error('Cloud analysis failed after retries:', lastError);
    throw lastError;
  }
  
  async verifyUrls(urls) {
    // FREE Layer 1: Check URLs against PhishTank/Google Safe Browsing
    try {
      return await this.apiCallViaBackground(`${this.apiUrl}/api/v1/verify-urls`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-License-Key': this.licenseKey || ''
        },
        body: JSON.stringify({ urls })
      });
    } catch (error) {
      console.warn('URL verification error:', error.message);
      return null; // Continue to next layer if URL check fails
    }
  }
  
  // Route API calls through background script to bypass LinkedIn's CSP
  async apiCallViaBackground(url, options) {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        { type: 'API_CALL', url, options },
        (response) => {
          if (chrome.runtime.lastError) {
            reject(new Error(chrome.runtime.lastError.message));
          } else if (response && response.success) {
            resolve(response.data);
          } else {
            reject(new Error(response?.error || 'API call failed'));
          }
        }
      );
    });
  }
}

// Export for use in extension
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CloudAnalyzer, FeatureExtractor };
}
