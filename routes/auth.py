import re
import json
import pyotp
import qrcode
import qrcode.constants
import io
import base64
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User, UserOAuth
from services.auth_service import validate_registration, generate_recovery_codes

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('feed.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return render_template('auth/login.html')

        if user.is_banned:
            flash(f'Your account has been banned. Reason: {user.ban_reason}', 'error')
            return render_template('auth/login.html')

        # Check if 2FA is enabled
        if user.has_2fa:
            session['2fa_user_id'] = user.id
            session['2fa_remember'] = remember
            return redirect(url_for('auth.verify_2fa'))

        login_user(user, remember=remember)
        user.last_active = db.func.now()
        db.session.commit()

        next_page = request.args.get('next')
        return redirect(next_page or url_for('feed.index'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('feed.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        display_name = request.form.get('display_name', '').strip()

        # Validation
        errors = validate_registration(username, email, password, confirm)
        if errors:
            for err in errors:
                flash(err, 'error')
            return render_template('auth/register.html')

        # Create user
        user = User(
            username=username,
            email=email,
            display_name=display_name or username,
        )
        user.set_password(password)

        # First user is admin
        if User.query.count() == 0:
            user.role = 'admin'

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash('Welcome to Socioprogram! Your account has been created.', 'success')
        return redirect(url_for('feed.index'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out.', 'info')
    return redirect(url_for('auth.login'))


# ── 2FA ──────────────────────────────────────────────

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        secret = session.get('2fa_setup_secret')

        if not secret:
            flash('2FA setup session expired. Try again.', 'error')
            return redirect(url_for('auth.setup_2fa'))

        totp = pyotp.TOTP(secret)
        if totp.verify(code):
            current_user.totp_secret = secret
            recovery = generate_recovery_codes()
            current_user.recovery_codes = json.dumps(recovery)
            db.session.commit()
            session.pop('2fa_setup_secret', None)
            flash('Two-factor authentication has been enabled!', 'success')
            return render_template('auth/setup_2fa.html', recovery_codes=recovery, step='recovery')
        else:
            flash('Invalid code. Please try again.', 'error')
            return redirect(url_for('auth.setup_2fa'))

    # Generate new TOTP secret
    secret = pyotp.random_base32()
    session['2fa_setup_secret'] = secret
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.email, issuer_name='Socioprogram')

    # Generate QR code as base64 image
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=6, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color='white', back_color='#0d1117')
    buffer = io.BytesIO()
    img.save(buffer, kind='PNG')  # type: ignore[call-arg]
    qr_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return render_template('auth/setup_2fa.html', qr_code=qr_b64, secret=secret, step='setup')


@auth_bp.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    user_id = session.get('2fa_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        user = db.session.get(User, user_id)

        if not user:
            session.pop('2fa_user_id', None)
            return redirect(url_for('auth.login'))

        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(code, valid_window=1):
            remember = session.pop('2fa_remember', False)
            session.pop('2fa_user_id', None)
            login_user(user, remember=remember)
            user.last_active = db.func.now()
            db.session.commit()
            return redirect(url_for('feed.index'))

        # Check recovery codes
        try:
            recovery = json.loads(user.recovery_codes or '[]')
        except (json.JSONDecodeError, TypeError):
            recovery = []
        if code in recovery:
            recovery.remove(code)
            user.recovery_codes = json.dumps(recovery)
            remember = session.pop('2fa_remember', False)
            session.pop('2fa_user_id', None)
            login_user(user, remember=remember)
            db.session.commit()
            flash('Recovery code used. You have {} remaining.'.format(len(recovery)), 'warning')
            return redirect(url_for('feed.index'))

        flash('Invalid authentication code.', 'error')

    return render_template('auth/verify_2fa.html')


@auth_bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    current_user.totp_secret = None
    current_user.recovery_codes = ''
    db.session.commit()
    flash('Two-factor authentication has been disabled.', 'info')
    return redirect(url_for('profile.edit'))


# ── OAuth SSO ────────────────────────────────────────

@auth_bp.route('/oauth/<provider>')
def oauth_login(provider):
    """Initiate OAuth flow for the given provider."""
    from services.auth_service import get_oauth_client
    client = get_oauth_client(provider)
    if not client:
        flash(f'{provider.title()} sign-in is not configured.', 'error')
        return redirect(url_for('auth.login'))

    redirect_uri = url_for('auth.oauth_callback', provider=provider, _external=True)
    return client.authorize_redirect(redirect_uri)


@auth_bp.route('/callback/<provider>')
def oauth_callback(provider):
    """Handle OAuth callback."""
    from services.auth_service import get_oauth_client, get_oauth_user_info
    client = get_oauth_client(provider)
    if not client:
        flash(f'{provider.title()} sign-in is not configured.', 'error')
        return redirect(url_for('auth.login'))

    try:
        token = client.authorize_access_token()
    except Exception:
        flash(f'Authentication with {provider.title()} failed.', 'error')
        return redirect(url_for('auth.login'))

    user_info = get_oauth_user_info(provider, client, token)
    if not user_info:
        flash(f'Could not retrieve your {provider.title()} profile.', 'error')
        return redirect(url_for('auth.login'))

    provider_id = str(user_info['id'])
    email = user_info.get('email', '')
    name = user_info.get('name', '')
    username_hint = user_info.get('username', '')

    # Check if OAuth account already linked
    oauth = UserOAuth.query.filter_by(provider=provider, provider_user_id=provider_id).first()

    if oauth:
        user = oauth.user
        if user.is_banned:
            flash(f'Your account has been banned. Reason: {user.ban_reason}', 'error')
            return redirect(url_for('auth.login'))
        login_user(user)
        user.last_active = db.func.now()
        db.session.commit()
        return redirect(url_for('feed.index'))

    # If user is already logged in, link the account
    if current_user.is_authenticated:
        new_oauth = UserOAuth(
            user_id=current_user.id,
            provider=provider,
            provider_user_id=provider_id,
            access_token=token.get('access_token', ''),
        )
        if provider == 'github' and username_hint:
            current_user.github_username = username_hint
        elif provider == 'reddit' and username_hint:
            current_user.reddit_username = username_hint
        db.session.add(new_oauth)
        db.session.commit()
        flash(f'{provider.title()} account linked successfully!', 'success')
        return redirect(url_for('profile.edit'))

    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first() if email else None
    if existing_user:
        new_oauth = UserOAuth(
            user_id=existing_user.id,
            provider=provider,
            provider_user_id=provider_id,
            access_token=token.get('access_token', ''),
        )
        db.session.add(new_oauth)
        login_user(existing_user)
        existing_user.last_active = db.func.now()
        db.session.commit()
        return redirect(url_for('feed.index'))

    # Create new user from OAuth
    base_username = re.sub(r'[^a-z0-9]', '', (username_hint or name or 'user').lower())[:24]
    username = base_username
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f'{base_username}{counter}'
        counter += 1

    user = User(
        username=username,
        email=email or f'{provider}_{provider_id}@oauth.local',
        display_name=name or username,
    )
    if provider == 'github':
        user.github_username = username_hint or ''
    elif provider == 'reddit':
        user.reddit_username = username_hint or ''

    if User.query.count() == 0:
        user.role = 'admin'

    db.session.add(user)
    db.session.flush()

    new_oauth = UserOAuth(
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_id,
        access_token=token.get('access_token', ''),
    )
    db.session.add(new_oauth)
    db.session.commit()

    login_user(user)
    flash('Welcome to Socioprogram! Your account has been created.', 'success')
    return redirect(url_for('feed.index'))
