from datetime import datetime, timezone
from models import db


class Notification(db.Model):
    """User notifications for stars, comments, follows, and mod actions."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(32), nullable=False)
    # Types: 'star' | 'comment' | 'follow' | 'mention' | 'mod_action' | 'warning'
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(512), default='')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def time_ago(self):
        now = datetime.now(timezone.utc)
        diff = now - self.created_at.replace(tzinfo=timezone.utc) if self.created_at.tzinfo is None else now - self.created_at
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            return f'{seconds // 60}m ago'
        elif seconds < 86400:
            return f'{seconds // 3600}h ago'
        else:
            return f'{seconds // 86400}d ago'

    def __repr__(self):
        return f'<Notification #{self.id} [{self.type}] for User #{self.user_id}>'
