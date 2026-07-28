from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.post import Post
from models.comment import Comment
from models.social import Star, Follow
from models.notification import Notification
from models.moderation import Report

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ── Stars ────────────────────────────────────────────

@api_bp.route('/posts/<int:post_id>/star', methods=['POST'])
@login_required
def toggle_star(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Star.query.filter_by(post_id=post_id, user_id=current_user.id).first()

    if existing:
        db.session.delete(existing)
        post.star_count = max(0, post.star_count - 1)
        db.session.commit()
        return jsonify({'starred': False, 'count': post.star_count})
    else:
        star = Star(post_id=post_id, user_id=current_user.id)
        db.session.add(star)
        post.star_count += 1
        db.session.commit()

        # Notify post author (if not self)
        if post.author_id != current_user.id:
            notif = Notification(
                user_id=post.author_id,
                type='star',
                message=f'@{current_user.username} starred your post "{post.title[:50]}"',
                link=f'/post/{post.id}',
            )
            db.session.add(notif)
            db.session.commit()

        return jsonify({'starred': True, 'count': post.star_count})


# ── Comments ─────────────────────────────────────────

@api_bp.route('/posts/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    code_snippet = request.form.get('code_snippet', '').strip()
    parent_id = request.form.get('parent_id', type=int)

    if not content:
        return jsonify({'error': 'Comment cannot be empty.'}), 400
    if len(content) > 2000:
        return jsonify({'error': 'Comment too long (max 2000 chars).'}), 400

    # Validate parent exists and belongs to same post
    if parent_id:
        parent = Comment.query.get(parent_id)
        if not parent or parent.post_id != post_id:
            parent_id = None

    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=content,
        code_snippet=code_snippet,
        parent_id=parent_id,
    )
    db.session.add(comment)
    post.comment_count += 1
    db.session.commit()

    # Notify post author
    if post.author_id != current_user.id:
        notif = Notification(
            user_id=post.author_id,
            type='comment',
            message=f'@{current_user.username} commented on "{post.title[:50]}"',
            link=f'/post/{post.id}',
        )
        db.session.add(notif)
        db.session.commit()

    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'code_snippet': comment.code_snippet,
        'author': current_user.username,
        'author_avatar': current_user.avatar_url,
        'display_name': current_user.display_name,
        'time_ago': comment.time_ago,
        'parent_id': comment.parent_id,
    })


@api_bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author_id != current_user.id and not current_user.is_moderator:
        return jsonify({'error': 'Unauthorized.'}), 403

    post = Post.query.get(comment.post_id)
    if post:
        post.comment_count = max(0, post.comment_count - 1)

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'deleted': True})


# ── Follow ───────────────────────────────────────────

@api_bp.route('/users/<int:user_id>/follow', methods=['POST'])
@login_required
def toggle_follow(user_id):
    if user_id == current_user.id:
        return jsonify({'error': 'You cannot follow yourself.'}), 400

    from models.user import User
    target = User.query.get_or_404(user_id)
    existing = Follow.query.filter_by(
        follower_id=current_user.id, following_id=user_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'following': False})
    else:
        follow = Follow(follower_id=current_user.id, following_id=user_id)
        db.session.add(follow)

        notif = Notification(
            user_id=user_id,
            type='follow',
            message=f'@{current_user.username} started following you',
            link=f'/profile/{target.username}',
        )
        db.session.add(notif)
        db.session.commit()
        return jsonify({'following': True})


# ── Reports ──────────────────────────────────────────

@api_bp.route('/report', methods=['POST'])
@login_required
def submit_report():
    post_id = request.form.get('post_id', type=int)
    comment_id = request.form.get('comment_id', type=int)
    reported_user_id = request.form.get('user_id', type=int)
    reason = request.form.get('reason', '').strip()
    details = request.form.get('details', '').strip()

    if not reason:
        return jsonify({'error': 'Please select a reason.'}), 400

    report = Report(
        reporter_id=current_user.id,
        post_id=post_id,
        comment_id=comment_id,
        reported_user_id=reported_user_id,
        reason=reason,
        details=details,
    )
    db.session.add(report)
    db.session.commit()

    # Auto-hide: if 3+ reports on same post, flag it
    if post_id:
        report_count = Report.query.filter_by(post_id=post_id, status='pending').count()
        if report_count >= 3:
            post = Post.query.get(post_id)
            if post and not post.is_removed:
                post.is_removed = True
                post.removed_reason = 'Auto-hidden: multiple reports pending review.'
                db.session.commit()

    return jsonify({'submitted': True, 'message': 'Report submitted. Thank you.'})


# ── Notifications ────────────────────────────────────

@api_bp.route('/notifications/count')
@login_required
def notification_count():
    from models.notification import Notification
    count = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()
    return jsonify({'count': count})


@api_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({'marked': True})
