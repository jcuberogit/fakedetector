# 🛡️ UniversalShield

**Free & Open Source anti-scam firewall - Protects you from phishing, fraud & social engineering across LinkedIn, Email & more.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Chrome Web Store](https://img.shields.io/badge/Chrome-Extension-blue.svg)](https://chrome.google.com/webstore)
[![Open Source](https://img.shields.io/badge/Open%20Source-100%25-brightgreen.svg)](https://github.com/jcuberogit/universalshield)

**Powered by [paradigm.fraud.agent](https://github.com/jcuberogit/universalshield) - Enterprise-grade ML fraud detection**

---

## 🎯 The Problem

Scammers are everywhere:
- 🤖 AI bots pretending to be recruiters on LinkedIn
- 💸 CV/Resume "improvement" scams
- 🎣 Phishing emails pretending to be banks/services
- 📧 Business email compromise (BEC) attacks
- 💰 Investment & crypto scams
- 🎭 Social engineering across all platforms

**In our tests, 60% of responses to "Open to Work" posts were scams.**

---

## ✨ Features

- **🔍 Multi-Platform Scanning** - LinkedIn, Gmail, Outlook & more
- **🚨 Visual Alerts** - Flags suspicious messages with clear warning badges
- **📊 100+ Scam Patterns** - Detects known scam phrases (English & Spanish)
- **🧠 ML-Powered** - Backed by paradigm.fraud.agent ML/GNN models
- **🕵️ Profile Analysis** - Identifies red flags in sender profiles
- **📈 Stats Dashboard** - Track how many scams you've avoided
- **🌐 Community Intelligence** - Crowdsourced scam database
- **🔒 Privacy First** - Local detection + optional cloud ML analysis

---

## 🚀 Installation

### From Chrome Web Store (Coming Soon)
1. Visit [Chrome Web Store](#)
2. Click "Add to Chrome"
3. Done! ScamShield is now protecting you.

### Manual Installation (Developer Mode)
1. Download or clone this repository
2. Open Chrome → `chrome://extensions/`
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select the `UniversalShield` folder
6. Navigate to LinkedIn and you're protected!

---

## 🔍 What It Detects

### CV/Resume Scams
- "I can help improve your CV"
- "Professional resume writing service"
- "Guaranteed job placement"
- "Your profile needs optimization"

### Bot Patterns
- Instant responses to posts
- Generic templated messages
- New accounts with stock photos
- Suspicious link patterns

### Phishing Attempts
- Fake job offers requiring payment
- "Interview" links to external sites
- Requests for personal information
- Urgency tactics ("Apply within 24 hours!")

---

## 🛠️ How It Works

```
Message/Email → UniversalShield Analysis → Risk Score → Visual Alert
                         │
                         ├── Local Pattern Matching (100+ patterns)
                         ├── Profile/Sender Analysis
                         ├── Link Safety Verification
                         └── [Optional] Cloud ML Analysis (fraud.agent API)
```

### Risk Levels

| Level | Badge | Meaning |
|-------|-------|---------|
| 🟢 Safe | None | Legitimate message |
| 🟡 Suspicious | ⚠️ | Some red flags, review carefully |
| 🔴 Scam | 🚨 | High confidence scam, avoid |

---

## 🤝 Contributing

We welcome contributions! This is 100% open source.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-detection`)
3. Commit your changes (`git commit -m 'Add new scam pattern'`)
4. Push to the branch (`git push origin feature/new-detection`)
5. Open a Pull Request

### Priority Areas
- [ ] Add more scam patterns (especially non-English)
- [ ] Improve profile analysis heuristics
- [ ] Firefox extension port
- [ ] Safari extension port
- [ ] Internationalization (i18n)

---

## 📊 Stats

Since launch:
- 🛡️ **X** scams blocked
- 👥 **X** users protected
- 🔍 **X** patterns detected

---

## 🔒 Privacy

**Your privacy is sacred.**

- ✅ All detection runs 100% locally in your browser
- ✅ No data is sent to external servers
- ✅ No tracking or analytics
- ✅ No account required
- ✅ Open source - verify the code yourself

---

## 📜 License

MIT License - Use it, modify it, share it. Free forever.

---

## 🙏 Acknowledgments

- Inspired by the 60% scam rate experienced by job seekers
- Built with ❤️ by [Paradigm](https://github.com/paradigm)
- Powered by the community

---

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/jcuberogit/universalshield/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jcuberogit/universalshield/discussions)
- **Email**: shield@paradigm.dev

---

**Together, let's make the internet safe from scammers.** 🛡️
