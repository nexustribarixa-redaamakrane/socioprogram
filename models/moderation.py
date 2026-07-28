from datetime import datetime, timezone
from models import db


class Ban(db.Model):
    """Ban record. All bans are public for transparency."""
    __tablename__ = 'bans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    banned_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    ban_type = db.Column(db.String(16), nullable=False)  # 'temporary' | 'permanent'
    duration_days = db.Column(db.Integer, nullable=True)  # For temporary bans
    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='bans_received')
    banned_by = db.relationship('User', foreign_keys=[banned_by_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Ban #{self.id} User #{self.user_id} [{self.ban_type}]>'


class Report(db.Model):
    """User-submitted reports against posts, comments, or users."""
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reason = db.Column(db.String(128), nullable=False)  # Rule category
    details = db.Column(db.Text, default='')
    status = db.Column(db.String(16), default='pending')
    # Status: 'pending' | 'reviewed' | 'actioned' | 'dismissed'
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    review_notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id])
    reported_user = db.relationship('User', foreign_keys=[reported_user_id])
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])
    post = db.relationship('Post', backref='reports')
    comment = db.relationship('Comment', backref='reports')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Report #{self.id} [{self.status}]>'


class Rule(db.Model):
    """Community rules. Displayed publicly, referenced in reports and bans."""
    __tablename__ = 'rules'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(16), nullable=False)  # 'warning' | 'temp_ban' | 'perm_ban'
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<Rule #{self.id} "{self.title}">'
