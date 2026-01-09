# 🛡️ LinkedIn ScamShield

**Free & Open Source Chrome extension to protect job seekers from LinkedIn scams.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Chrome Web Store](https://img.shields.io/badge/Chrome-Extension-blue.svg)](https://chrome.google.com/webstore)
[![Open Source](https://img.shields.io/badge/Open%20Source-100%25-brightgreen.svg)](https://github.com/paradigm/linkedin-scamshield)

---

## 🎯 The Problem

When you set your LinkedIn status to "Open to Work", you get flooded with:
- 🤖 AI bots pretending to be recruiters
- 💸 CV/Resume "improvement" scams
- 🎣 Phishing messages with fake job offers
- 📧 Lead generation spam disguised as opportunities

**In our tests, 60% of responses to "Open to Work" posts were scams.**

---

## ✨ Features

- **🔍 Real-time Scanning** - Automatically scans LinkedIn messages and connection requests
- **🚨 Visual Alerts** - Flags suspicious messages with clear warning badges
- **📊 Scam Patterns** - Detects 50+ known scam phrases and patterns
- **🕵️ Profile Analysis** - Identifies red flags in sender profiles
- **📈 Stats Dashboard** - Track how many scams you've avoided
- **🌐 Community Blocklist** - Crowdsourced database of known scammers
- **🔒 Privacy First** - All detection runs locally, no data sent to servers

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
5. Select the `LinkedIn-ScamShield` folder
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
LinkedIn Message → ScamShield Analysis → Risk Score → Visual Alert
                         │
                         ├── Keyword Detection (50+ patterns)
                         ├── Profile Age Analysis
                         ├── Network Pattern Check
                         └── Link Safety Verification
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

- **Issues**: [GitHub Issues](https://github.com/jcuberogit/LinkedIn-ScamShield/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jcuberogit/LinkedIn-ScamShield/discussions)
- **Email**: scamshield@paradigm.dev

---

**Together, let's make LinkedIn safe for job seekers.** 🛡️
