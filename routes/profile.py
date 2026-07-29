import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.user import User
from models.post import Post
from models.social import Star, Follow, Bookmark, Repost

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('/<username>')
def view(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'posts')

    if tab == 'stars':
        starred_post_ids = [s.post_id for s in Star.query.filter_by(user_id=user.id).all()]
        pagination = Post.query.filter(
            Post.id.in_(starred_post_ids), Post.is_removed == False
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    elif tab == 'bookmarks':
        bm_post_ids = [b.post_id for b in Bookmark.query.filter_by(user_id=user.id).all()]
        pagination = Post.query.filter(
            Post.id.in_(bm_post_ids), Post.is_removed == False
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    elif tab == 'reposts':
        rp_post_ids = [r.post_id for r in Repost.query.filter_by(user_id=user.id).all()]
        pagination = Post.query.filter(
            Post.id.in_(rp_post_ids), Post.is_removed == False
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    elif tab == 'projects':
        pagination = Post.query.filter_by(
            author_id=user.id, is_removed=False
        ).filter(
            Post.post_type.in_(['project', 'showcase'])
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    elif tab == 'snippets':
        pagination = Post.query.filter_by(
            author_id=user.id, post_type='snippet', is_removed=False
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    else:
        pagination = Post.query.filter_by(
            author_id=user.id, is_removed=False
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=20, error_out=False)

    # Contribution stats
    follower_count = Follow.query.filter_by(following_id=user.id).count()
    following_count = Follow.query.filter_by(follower_id=user.id).count()
    stats = {
        'total_posts': Post.query.filter_by(author_id=user.id, is_removed=False).count(),
        'total_stars_received': db.session.query(db.func.sum(Post.star_count)).filter(
            Post.author_id == user.id
        ).scalar() or 0,
        'total_snippets': Post.query.filter_by(
            author_id=user.id, post_type='snippet', is_removed=False
        ).count(),
        'followers_count': follower_count,
        'following_count': following_count,
    }

    # Generate 52-week activity heatmap representation (52 blocks)
    # Simple simulated activity level (0-4) based on recent posts
    activity_grid = []
    user_posts = Post.query.filter_by(author_id=user.id).all()
    post_count = len(user_posts)
    for i in range(52):
        if post_count == 0:
            level = 0
        elif i == 51:
            level = min(4, post_count)
        elif i % 7 == 0 and post_count > 2:
            level = (i % 3) + 1
        else:
            level = (i % 2) if post_count > 5 else 0
        activity_grid.append(level)

    is_following = False
    if current_user.is_authenticated and current_user.id != user.id:
        is_following = Follow.query.filter_by(
            follower_id=current_user.id, following_id=user.id
        ).first() is not None

    return render_template('profile/view.html',
                           profile_user=user,
                           posts=pagination.items,
                           pagination=pagination,
                           tab=tab,
                           stats=stats,
                           activity_grid=activity_grid,
                           is_following=is_following)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        display_name = request.form.get('display_name', '').strip()
        bio = request.form.get('bio', '').strip()
        tech_stack = request.form.get('tech_stack', '').strip()
        website = request.form.get('website', '').strip()
        location = request.form.get('location', '').strip()
        github_username = request.form.get('github_username', '').strip()
        reddit_username = request.form.get('reddit_username', '').strip()

        if display_name:
            current_user.display_name = display_name[:64]
        if len(bio) <= 500:
            current_user.bio = bio
        current_user.tech_stack = tech_stack[:256]
        current_user.website = website[:256]
        current_user.location = location[:128]
        current_user.github_username = github_username[:64]
        current_user.reddit_username = reddit_username[:64]

        allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})

        # Handle avatar upload
        file = request.files.get('avatar')
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if ext in allowed:
                filename = f'{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}'
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
                os.makedirs(upload_dir, exist_ok=True)
                if current_user.avatar_path:
                    old_path = os.path.join(upload_dir, current_user.avatar_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                file.save(os.path.join(upload_dir, filename))
                current_user.avatar_path = filename

        # Handle banner upload
        banner_file = request.files.get('banner')
        if banner_file and banner_file.filename:
            ext = banner_file.filename.rsplit('.', 1)[1].lower() if '.' in banner_file.filename else ''
            if ext in allowed:
                filename = f'banner_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}'
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'banners')
                os.makedirs(upload_dir, exist_ok=True)
                if current_user.banner_path:
                    old_path = os.path.join(upload_dir, current_user.banner_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                banner_file.save(os.path.join(upload_dir, filename))
                current_user.banner_path = filename

        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('profile.view', username=current_user.username))

    return render_template('profile/edit.html')


@profile_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password', '')
    new_pw = request.form.get('new_password', '')
    confirm_pw = request.form.get('confirm_password', '')

    if not current_user.check_password(current_pw):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('profile.edit'))
    if len(new_pw) < 8:
        flash('New password must be at least 8 characters.', 'error')
        return redirect(url_for('profile.edit'))
    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('profile.edit'))

    current_user.set_password(new_pw)
    db.session.commit()
    flash('Password changed successfully.', 'success')
    return redirect(url_for('profile.edit'))


@profile_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    password = request.form.get('password', '')
    if not current_user.check_password(password):
        flash('Incorrect password. Account not deleted.', 'error')
        return redirect(url_for('profile.edit'))

    db.session.delete(current_user)
    db.session.commit()
    flash('Your account has been deleted.', 'info')
    return redirect(url_for('auth.login'))
