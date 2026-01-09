/**
 * LinkedIn ScamShield - Scam Detection Patterns
 * 100% Open Source - MIT License
 * 
 * This file contains all the patterns used to detect scams.
 * Community contributions welcome!
 */

const ScamPatterns = {
  // CV/Resume Improvement Scams
  cvScams: [
    'improve your cv',
    'improve your resume',
    'cv improvement',
    'resume improvement',
    'professional resume writing',
    'cv writing service',
    'resume writing service',
    'optimize your cv',
    'optimize your resume',
    'cv optimization',
    'resume optimization',
    'rewrite your cv',
    'rewrite your resume',
    'cv makeover',
    'resume makeover',
    'transform your cv',
    'transform your resume',
    'boost your cv',
    'boost your resume',
    'enhance your cv',
    'enhance your resume',
    'polish your cv',
    'polish your resume',
    'revamp your cv',
    'revamp your resume',
    'ats-friendly cv',
    'ats-friendly resume',
    'ats optimized',
    'beat the ats',
    'pass ats systems',
    'linkedin profile optimization',
    'optimize your linkedin',
    'linkedin makeover'
  ],

  // Fake Job Offer Patterns
  fakeJobOffers: [
    'guaranteed job placement',
    'guaranteed employment',
    '100% job guarantee',
    'we have a job for you',
    'job waiting for you',
    'immediate start',
    'start immediately',
    'no experience needed',
    'no experience required',
    'work from home opportunity',
    'easy money',
    'make money fast',
    'high paying job',
    'earn \$',
    'earn up to \$',
    'unlimited earning potential',
    'be your own boss',
    'financial freedom',
    'passive income'
  ],

  // Urgency Tactics
  urgencyTactics: [
    'limited time offer',
    'act now',
    'apply within 24 hours',
    'only a few spots left',
    'exclusive opportunity',
    'don\'t miss out',
    'time sensitive',
    'urgent response needed',
    'respond immediately',
    'limited availability',
    'offer expires',
    'last chance'
  ],

  // Payment Request Red Flags
  paymentRedFlags: [
    'small fee',
    'one-time fee',
    'registration fee',
    'processing fee',
    'application fee',
    'training fee',
    'material fee',
    'pay to start',
    'investment required',
    'initial investment',
    'deposit required',
    'send money',
    'wire transfer',
    'western union',
    'moneygram',
    'gift card',
    'bitcoin payment',
    'crypto payment'
  ],

  // Generic/Bot Patterns
  botPatterns: [
    'i came across your profile',
    'i noticed your profile',
    'your profile caught my attention',
    'i was impressed by your profile',
    'i found your profile interesting',
    'i saw that you\'re open to work',
    'i noticed you\'re looking for opportunities',
    'perfect candidate',
    'ideal candidate',
    'you\'re exactly what we\'re looking for',
    'exciting opportunity',
    'amazing opportunity',
    'incredible opportunity',
    'life-changing opportunity'
  ],

  // Phishing Indicators
  phishingIndicators: [
    'click here to apply',
    'click the link below',
    'fill out this form',
    'complete this survey',
    'verify your identity',
    'confirm your details',
    'update your information',
    'login to continue',
    'enter your password',
    'provide your ssn',
    'social security number',
    'bank account details',
    'credit card information'
  ],

  // Spanish Scam Patterns (Latinoamérica)
  spanishPatterns: [
    'mejorar tu cv',
    'mejorar tu curriculum',
    'mejora tu hoja de vida',
    'optimizar tu perfil',
    'oportunidad de empleo garantizada',
    'trabajo desde casa',
    'gana dinero fácil',
    'ingresos pasivos',
    'libertad financiera',
    'oferta limitada',
    'no dejes pasar esta oportunidad',
    'cupo limitado'
  ],

  // Suspicious Domains (partial matches)
  suspiciousDomains: [
    'bit.ly',
    'tinyurl',
    'shorturl',
    't.co',
    'goo.gl',
    'rebrand.ly',
    'clickmeter',
    'linktr.ee',
    'forms.gle',
    'typeform.com',
    'jotform.com',
    'calendly.com/random',
    'zoom.us/j/fake'
  ]
};

// Risk weights for different pattern types
const RiskWeights = {
  cvScams: 0.8,
  fakeJobOffers: 0.9,
  urgencyTactics: 0.5,
  paymentRedFlags: 1.0,
  botPatterns: 0.4,
  phishingIndicators: 0.9,
  spanishPatterns: 0.7,
  suspiciousDomains: 0.6
};

// Export for use in content script
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ScamPatterns, RiskWeights };
}
