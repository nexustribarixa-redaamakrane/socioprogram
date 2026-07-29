import os
import re
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import bleach
from models import db
from models.post import Post, Tag
from models.comment import Comment
from models.social import Star
from models.notification import Notification

posts_bp = Blueprint('posts', __name__, url_prefix='/post')

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'code', 'pre', 'a', 'ul', 'ol', 'li', 'blockquote', 'h3', 'h4']
ALLOWED_ATTRS = {'a': ['href', 'title'], 'code': ['class']}


def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.is_banned:
        flash('Your account is banned. You cannot create posts.', 'error')
        return redirect(url_for('feed.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        post_type = request.form.get('post_type', 'discussion')
        code_snippet = request.form.get('code_snippet', '').strip()
        code_language = request.form.get('code_language', '').strip()
        external_url = request.form.get('external_url', '').strip()

        # Validation
        if not title or len(title) < 5:
            flash('Title must be at least 5 characters.', 'error')
            return render_template('posts/create.html')
        if len(title) > 200:
            flash('Title must be 200 characters or fewer.', 'error')
            return render_template('posts/create.html')
        if post_type not in ('project', 'snippet', 'discussion', 'showcase', 'shill'):
            post_type = 'discussion'

        # Sanitize content
        content = bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)

        # Handle screenshot upload
        screenshot_path = ''
        file = request.files.get('screenshot')
        if file and file.filename and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f'{uuid.uuid4().hex}.{ext}'
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'posts')
            os.makedirs(upload_dir, exist_ok=True)
            file.save(os.path.join(upload_dir, filename))
            screenshot_path = filename

        # Extract hashtags from title, content, and form tags input
        raw_tags = set(re.findall(r'#(\w+)', title + ' ' + content))
        custom_tags = request.form.get('tags', '').strip()
        if custom_tags:
            for t in custom_tags.split(','):
                cleaned = t.strip().lstrip('#').lower()
                if cleaned:
                    raw_tags.add(cleaned)

        tag_objs = []
        for tag_name in raw_tags:
            tag_name_clean = tag_name.lower()[:32]
            tag_obj = Tag.query.filter_by(name=tag_name_clean).first()
            if not tag_obj:
                tag_obj = Tag(name=tag_name_clean)
                db.session.add(tag_obj)
            tag_objs.append(tag_obj)

        post = Post(
            author_id=current_user.id,
            title=title,
            content=content,
            post_type=post_type,
            code_snippet=code_snippet,
            code_language=code_language,
            external_url=external_url,
            screenshot_path=screenshot_path,
            source='original',
        )
        post.tags = tag_objs
        db.session.add(post)
        db.session.commit()

        flash('Post published!', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))

    return render_template('posts/create.html')


@posts_bp.route('/<int:post_id>')
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    if post.is_removed and not (current_user.is_authenticated and current_user.is_moderator):
        flash('This post has been removed by a moderator.', 'error')
        return redirect(url_for('feed.index'))

    # Get top-level comments (not replies)
    comments = Comment.query.filter_by(
        post_id=post_id, parent_id=None, is_removed=False
    ).order_by(Comment.created_at.asc()).all()

    # Check if current user starred this post
    user_starred = False
    if current_user.is_authenticated:
        user_starred = Star.query.filter_by(
            post_id=post_id, user_id=current_user.id
        ).first() is not None

    return render_template('posts/detail.html',
                           post=post,
                           comments=comments,
                           user_starred=user_starred)


@posts_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id and not current_user.is_moderator:
        flash('You can only delete your own posts.', 'error')
        return redirect(url_for('posts.detail', post_id=post_id))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('feed.index'))
