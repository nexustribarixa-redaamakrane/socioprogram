from datetime import datetime, timezone
from models import db


class Post(db.Model):
    """A user-created post or aggregated external content."""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_type = db.Column(db.String(32), default='discussion')
    # Types: 'project' | 'snippet' | 'discussion' | 'showcase' | 'shill'
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, default='')
    code_snippet = db.Column(db.Text, default='')
    code_language = db.Column(db.String(32), default='')
    external_url = db.Column(db.String(1024), default='')
    source = db.Column(db.String(16), default='original')  # 'original' | 'reddit' | 'github'
    screenshot_path = db.Column(db.String(512), default='')

    # Denormalized counters for performance
    star_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)

    # Moderation
    is_pinned = db.Column(db.Boolean, default=False)
    is_removed = db.Column(db.Boolean, default=False)
    removed_reason = db.Column(db.Text, default='')

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic',
                               cascade='all, delete-orphan')
    stars = db.relationship('Star', backref='post', lazy='dynamic',
                            cascade='all, delete-orphan')
    images = db.relationship('PostImage', backref='post', lazy='dynamic',
                             cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def screenshot_url(self):
        if self.screenshot_path:
            return f'/static/uploads/posts/{self.screenshot_path}'
        return ''

    @property
    def time_ago(self):
        """Human-readable relative time."""
        now = datetime.now(timezone.utc)
        diff = now - self.created_at.replace(tzinfo=timezone.utc) if self.created_at.tzinfo is None else now - self.created_at
        seconds = int(diff.total_seconds())
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            mins = seconds // 60
            return f'{mins}m ago'
        elif seconds < 86400:
            hours = seconds // 3600
            return f'{hours}h ago'
        elif seconds < 2592000:
            days = seconds // 86400
            return f'{days}d ago'
        else:
            return self.created_at.strftime('%b %d, %Y')

    def __repr__(self):
        return f'<Post #{self.id} "{self.title[:30]}">'


class PostImage(db.Model):
    """Additional images attached to a post."""
    __tablename__ = 'post_images'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    image_path = db.Column(db.String(512), nullable=False)
    caption = db.Column(db.String(256), default='')
    order = db.Column(db.Integer, default=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f'<PostImage #{self.id} for Post #{self.post_id}>'
