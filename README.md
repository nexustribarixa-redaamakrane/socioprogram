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
git clone https://github.com/youruser/socioprogram.git
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
