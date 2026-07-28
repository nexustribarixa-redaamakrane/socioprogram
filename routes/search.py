from flask import Blueprint, render_template, request, current_app
from models.post import Post
from models.user import User

search_bp = Blueprint('search', __name__, url_prefix='/search')


@search_bp.route('/')
def index():
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'posts')  # 'posts' or 'users'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 20)

    results = []
    pagination = None

    if query:
        if search_type == 'users':
            pagination = User.query.filter(
                User.username.ilike(f'%{query}%') | User.display_name.ilike(f'%{query}%')
            ).filter_by(is_banned=False).paginate(page=page, per_page=per_page, error_out=False)
            results = pagination.items
        else:
            pagination = Post.query.filter(
                (Post.title.ilike(f'%{query}%') | Post.content.ilike(f'%{query}%'))
                & (Post.is_removed == False)
            ).order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
            results = pagination.items

    return render_template('search/index.html',
                           query=query,
                           search_type=search_type,
                           results=results,
                           pagination=pagination)
