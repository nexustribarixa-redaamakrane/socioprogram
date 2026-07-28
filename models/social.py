from datetime import datetime, timezone
from models import db


class Star(db.Model):
    """Contribution appreciation — stars, NOT likes."""
    __tablename__ = 'stars'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='uq_star_post_user'),
    )

    def __repr__(self):
        return f'<Star User #{self.user_id} → Post #{self.post_id}>'


class Follow(db.Model):
    """Follow relationship between users (project-focused)."""
    __tablename__ = 'follows'

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('follower_id', 'following_id', name='uq_follow_pair'),
    )

    def __repr__(self):
        return f'<Follow #{self.follower_id} → #{self.following_id}>'
