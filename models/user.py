from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(UserMixin, db.Model):
    """Core user account. Contributions over clout."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)  # Null for OAuth-only accounts
    display_name = db.Column(db.String(64), nullable=False)
    bio = db.Column(db.Text, default='')
    avatar_path = db.Column(db.String(512), default='')
    github_username = db.Column(db.String(64), default='')
    reddit_username = db.Column(db.String(64), default='')
    role = db.Column(db.String(16), default='user')  # 'user' | 'moderator' | 'admin'
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.Text, default='')
    ban_until = db.Column(db.DateTime, nullable=True)  # Null = permanent if is_banned
    totp_secret = db.Column(db.String(32), nullable=True)  # 2FA secret
    recovery_codes = db.Column(db.Text, default='')  # JSON list of one-time codes
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic',
                            foreign_keys='Post.author_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic',
                               foreign_keys='Comment.author_id')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic',
                                    foreign_keys='Notification.user_id')
    oauth_accounts = db.relationship('UserOAuth', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @property
    def is_moderator(self):
        return self.role in ('moderator', 'admin')

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def has_2fa(self):
        return bool(self.totp_secret)

    @property
    def avatar_url(self):
        if self.avatar_path:
            return f'/static/uploads/avatars/{self.avatar_path}'
        # Default avatar — first letter of username
        return ''

    def __repr__(self):
        return f'<User @{self.username}>'


class UserOAuth(db.Model):
    """Linked OAuth accounts (Google, GitHub, Reddit)."""
    __tablename__ = 'user_oauth'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String(32), nullable=False)  # 'google' | 'github' | 'reddit'
    provider_user_id = db.Column(db.String(256), nullable=False)
    access_token = db.Column(db.String(512), default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_id'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<UserOAuth {self.provider}:{self.provider_user_id}>'
