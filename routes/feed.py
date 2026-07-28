from flask import Blueprint, render_template, request, current_app
from flask_login import current_user
from models.post import Post
from services.aggregator import get_aggregated_feed

feed_bp = Blueprint('feed', __name__)


@feed_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')
    per_page = current_app.config.get('POSTS_PER_PAGE', 20)

    # Build query for local posts — strict chronological order, no algorithm
    query = Post.query.filter_by(is_removed=False)

    if filter_type == 'projects':
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

    # Check which posts the current user has starred
    starred_ids = set()
    if current_user.is_authenticated:
        from models.social import Star
        user_stars = Star.query.filter(
            Star.user_id == current_user.id,
            Star.post_id.in_([p.id for p in pagination.items])
        ).all()
        starred_ids = {s.post_id for s in user_stars}

    return render_template('feed/index.html',
                           posts=pagination.items,
                           pagination=pagination,
                           filter_type=filter_type,
                           starred_ids=starred_ids)
