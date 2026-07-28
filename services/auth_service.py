import re
import secrets
from authlib.integrations.flask_client import OAuth
from flask import current_app

oauth = OAuth()

_oauth_initialized = False


def init_oauth(app):
    """Initialize OAuth clients. Called lazily on first use."""
    global _oauth_initialized
    if _oauth_initialized:
        return
    oauth.init_app(app)

    if app.config.get('GOOGLE_CLIENT_ID'):
        oauth.register(
            name='google',
            client_id=app.config['GOOGLE_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )

    if app.config.get('GITHUB_CLIENT_ID'):
        oauth.register(
            name='github',
            client_id=app.config['GITHUB_CLIENT_ID'],
            client_secret=app.config['GITHUB_CLIENT_SECRET'],
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'read:user user:email'},
        )

    if app.config.get('REDDIT_CLIENT_ID'):
        oauth.register(
            name='reddit',
            client_id=app.config['REDDIT_CLIENT_ID'],
            client_secret=app.config['REDDIT_CLIENT_SECRET'],
            access_token_url='https://www.reddit.com/api/v1/access_token',
            authorize_url='https://www.reddit.com/api/v1/authorize',
            api_base_url='https://oauth.reddit.com/',
            client_kwargs={'scope': 'identity'},
            access_token_params={'grant_type': 'authorization_code'},
        )

    _oauth_initialized = True


def get_oauth_client(provider):
    """Get the OAuth client for a provider, initializing if needed."""
    init_oauth(current_app._get_current_object())
    try:
        return getattr(oauth, provider, None)
    except AttributeError:
        return None


def get_oauth_user_info(provider, client, token):
    """Fetch user info from the OAuth provider."""
    try:
        if provider == 'google':
            resp = client.get('https://www.googleapis.com/oauth2/v3/userinfo', token=token)
            data = resp.json()
            return {
                'id': data.get('sub'),
                'email': data.get('email', ''),
                'name': data.get('name', ''),
                'username': data.get('email', '').split('@')[0],
            }

        elif provider == 'github':
            resp = client.get('user', token=token)
            data = resp.json()
            # Get email separately (may be private)
            email = data.get('email', '')
            if not email:
                email_resp = client.get('user/emails', token=token)
                emails = email_resp.json()
                for e in emails:
                    if e.get('primary'):
                        email = e.get('email', '')
                        break
            return {
                'id': data.get('id'),
                'email': email,
                'name': data.get('name', data.get('login', '')),
                'username': data.get('login', ''),
            }

        elif provider == 'reddit':
            resp = client.get('api/v1/me', token=token)
            data = resp.json()
            return {
                'id': data.get('id'),
                'email': '',  # Reddit doesn't share email
                'name': data.get('name', ''),
                'username': data.get('name', ''),
            }

    except Exception:
        return None

    return None


def validate_registration(username, email, password, confirm):
    """Validate registration fields. Returns list of error strings."""
    from models.user import User
    errors = []

    if not username or len(username) < 3 or len(username) > 32:
        errors.append('Username must be 3–32 characters.')
    elif not re.match(r'^[a-z0-9_]+$', username):
        errors.append('Username can only contain lowercase letters, numbers, and underscores.')
    elif User.query.filter_by(username=username).first():
        errors.append('This username is already taken.')

    if not email or '@' not in email:
        errors.append('Enter a valid email address.')
    elif User.query.filter_by(email=email).first():
        errors.append('An account with this email already exists.')

    if not password or len(password) < 8:
        errors.append('Password must be at least 8 characters.')
    elif not re.search(r'\d', password):
        errors.append('Password must contain at least one number.')
    elif not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~]', password):
        errors.append('Password must contain at least one special character.')

    if password != confirm:
        errors.append('Passwords do not match.')

    return errors


def generate_recovery_codes(count=8):
    """Generate one-time recovery codes for 2FA."""
    return [secrets.token_hex(4).upper() for _ in range(count)]
