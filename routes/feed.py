from flask import Blueprint, render_template, request, current_app
from flask_login import current_user
from models import db
from models.post import Post, Tag
from models.user import User

feed_bp = Blueprint('feed', __name__)


@feed_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')
    tag_name = request.args.get('tag', '').strip().lower()
    per_page = current_app.config.get('POSTS_PER_PAGE', 20)

    # Build query for local posts — strict chronological order, no algorithm
    query = Post.query.filter_by(is_removed=False)

    if tag_name:
        tag_obj = Tag.query.filter_by(name=tag_name).first()
        if tag_obj:
            query = query.filter(Post.tags.contains(tag_obj))
        else:
            query = query.filter(False)  # empty

    elif filter_type == 'projects':
        query = query.filter(Post.post_type.in_(['project', 'showcase']))
    elif filter_type == 'snippets':
        query = query.filter_by(post_type='snippet')
    elif filter_type == 'discussions':
        query = query.filter_by(post_type='discussion')
    elif filter_type == 'external':
        query = query.filter(Post.source.in_(['reddit', 'github']))

    # Chronological order — no engagement-based ranking
    query = query.order_by(Post.is_pinned.desc(), Post.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Check starred and bookmarked posts for current user
    starred_ids = set()
    bookmarked_ids = set()
    if current_user.is_authenticated:
        from models.social import Star, Bookmark
        post_ids = [p.id for p in pagination.items]
        if post_ids:
            starred_ids = {s.post_id for s in Star.query.filter(Star.user_id == current_user.id, Star.post_id.in_(post_ids)).all()}
            bookmarked_ids = {b.post_id for b in Bookmark.query.filter(Bookmark.user_id == current_user.id, Bookmark.post_id.in_(post_ids)).all()}

    # Sidebar data: Top Trending Tags & Suggested Contributors
    trending_tags = Tag.query.limit(8).all()
    suggested_users = User.query.filter(User.is_banned == False).order_by(User.id.desc()).limit(5).all()

    return render_template('feed/index.html',
                           posts=pagination.items,
                           pagination=pagination,
                           filter_type=filter_type,
                           tag_name=tag_name,
                           starred_ids=starred_ids,
                           bookmarked_ids=bookmarked_ids,
                           trending_tags=trending_tags,
                           suggested_users=suggested_users)
