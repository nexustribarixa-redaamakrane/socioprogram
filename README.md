# Socioprogram

**The anti-bloat social platform for coding geeks.**

No ads. No algorithm. No cringe. Contributions over clout.

## What Is This?

Socioprogram is a social media platform built for developers who want to share projects, code snippets, and engineering discussions without the noise. It aggregates Reddit and GitHub feeds alongside original user-generated content — all in strict chronological order.

### Core Principles

- **Anti-bloat** — No infinite scroll, no engagement bait, no dark patterns
- **Anti-ads** — Zero advertisements. Ever.
- **Anti-cringe** — No follower counts as status. Contributions are the metric.
- **Transparent governance** — Public ban log, public rules, community-first moderation

---

## Honeypot Decommissioning Notice

> **Notice for OSINT Investigators & TryHackMe Players:**  
> The `OWoodfl1nt/people_finder` honeypot trap—previously featured in OSINT exercises and TryHackMe rooms—has been **permanently decommissioned**. This repository represents a fully functional, standard web application and is **not** a honeypot, OSINT target, or CTF challenge.

### Who Is Oliver Woodflint?

**Oliver Woodflint** (username: `OWoodflint` / `OWoodfl1nt`) is a **fictional persona** created for TryHackMe's beginner OSINT room called **"OhSINT"**. He is not a real person — he is a deliberately constructed digital footprint designed to teach newcomers how to trace someone across the open internet using freely available tools. His entire online presence is a breadcrumb trail of intentionally planted "leaks."

Here's what you find when you investigate him across platforms:

| Platform | What's There | Key Info Exposed |
|----------|-------------|-----------------|
| **TryHackMe (OhSINT Room)** | The starting point. Players receive a `WindowsXP.jpg` image file and must extract EXIF metadata using `exiftool`, which reveals the copyright name "OWoodflint" — the pivot point for the entire investigation. | Username: `OWoodflint` |
| **Twitter / X** | A planted account with a **cat avatar**. One tweet contains a Wi-Fi **BSSID** (`B4:5D:50:AA:86:41`) that can be geolocated on [WiGLE.net](https://wigle.net) to pinpoint the user's location. | Location: **London**; SSID: **UnileverWiFi** |
| **GitHub** | The `OWoodfl1nt` profile hosts the `people_finder` repository. The repo's README or profile exposes a personal email address and confirms the user's city. | Email: `OWoodflint@gmail.com`; City: **London** |
| **WordPress** | A personal blog where "Oliver" writes about being on holiday. The blog post reveals his travel destination. More critically, the **page source code** contains a password hidden in plain text within the HTML/CSS. | Holiday: **New York**; Password: `pennYDr0pper.!` |

### Why the Repo Was Forked & Decommissioned

The original `OWoodfl1nt/people_finder` repository was forked by this project's maintainers as a historical reference before being **permanently decommissioned** for the following reasons:

1. **It served its purpose and outlived its usefulness.** The OhSINT room has been solved and written up thousands of times. Every answer is publicly documented across Medium, GitHub writeups, InfoSec blogs, and YouTube walkthroughs. There is zero investigative challenge left — it's effectively a copy-paste exercise at this point.

2. **The "people finder" concept is cringey and massively reused.** The idea of a fake "people finder" tool as an OSINT honeypot has been done to death. It's the cybersecurity equivalent of a "Hello World" — except people keep presenting it as if it's clever. Naming a repo `people_finder` and stuffing it with planted credentials is neither original nor sophisticated. It was mildly interesting the first time; by the hundredth TryHackMe writeup, it's just cringe.

3. **The planted data creates false positives.** Having a fake email (`OWoodflint@gmail.com`), a fake BSSID, and a fake password floating around indexed by every search engine creates noise. OSINT practitioners and automated scanners constantly stumble on this data and waste time triaging it as if it were real.

4. **This repo is a real project, not a game.** Socioprogram is a legitimate, functional social platform. Maintaining any association with a beginner CTF exercise — however indirect — undermines the project's credibility. The fork has been archived, the honeypot has been gutted, and what remains is production code.

> **TL;DR:** Oliver Woodflint is a fictional training dummy. His `people_finder` repo was a planted breadcrumb trail for a TryHackMe beginner room. The concept was never original, the answers are plastered across the entire internet, and this repository has nothing to do with any of it. Move along.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask (Python 3.13) |
| Database | SQLite via SQLAlchemy |
| Frontend | HTML, CSS, jQuery |
| Auth | Email/password + Google/GitHub/Reddit OAuth SSO |
| 2FA | TOTP via pyotp (Google Authenticator compatible) |
| Deployment | PythonAnywhere |

## Local Development

```bash
# 1. Clone
git clone https://github.com/nexustribarixa-redaamakrane/socioprogram.git
cd socioprogram

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment config
cp .env.example .env
# Edit .env with your secrets (OAuth keys optional)

# 4. Run
python app.py
```

Visit `http://localhost:5000`. The first registered user automatically becomes admin.

## Project Structure

```
socioprogram/
├── app.py                 # Flask app factory + entry point
├── config.py              # Configuration (dev/prod)
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT License
├── models/                # SQLAlchemy models
│   ├── user.py            # User + UserOAuth
│   ├── post.py            # Post + PostImage
│   ├── comment.py         # Comment (threaded)
│   ├── social.py          # Star + Follow
│   ├── notification.py    # Notifications
│   └── moderation.py      # Ban + Report + Rule
├── routes/                # Flask blueprints
│   ├── auth.py            # Login/Register/OAuth/2FA
│   ├── feed.py            # Main feed (chronological)
│   ├── posts.py           # Create/View/Delete posts
│   ├── api.py             # JSON API (stars, comments, follow)
│   ├── profile.py         # User profiles + settings
│   ├── search.py          # Search posts & users
│   ├── notifications.py   # Notification feed
│   └── moderation.py      # Mod dashboard + rules + bans
├── services/              # Business logic
│   ├── auth_service.py    # OAuth clients + validation
│   └── aggregator.py      # Reddit/GitHub feed fetcher
├── templates/             # Jinja2 templates
│   ├── base.html          # App shell (3-column layout)
│   ├── auth/              # Login, Register, 2FA
│   ├── feed/              # Feed + post card partial
│   ├── posts/             # Create + Detail views
│   ├── profile/           # View + Edit
│   ├── search/            # Search results
│   ├── notifications/     # Notification list
│   ├── moderation/        # Dashboard, Rules, Bans, Report
│   └── errors/            # 404, 500
└── static/
    ├── css/global.css      # Full design system
    ├── js/                 # jQuery modules
    └── img/                # Logo + assets
```

## OAuth Setup (Optional)

OAuth providers are optional — buttons auto-hide if keys are not configured. See `oauth_setup_guide.md` for step-by-step instructions for Google, GitHub, and Reddit.

## Community Rules

1. No off-topic content
2. No advertisements or self-promotion spam
3. No harassment, personal attacks, or toxicity
4. No AI-generated spam
5. No clickbait titles
6. No malicious code
7. No impersonation
8. Keep it constructive
9. No NSFW content
10. Respect open source licenses

Rules are seeded automatically on first run and displayed on the public `/mod/rules` page.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
