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


# ── Bookmarks ────────────────────────────────────────

@api_bp.route('/posts/<int:post_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(post_id):
    from models.social import Bookmark
    post = Post.query.get_or_404(post_id)
    existing = Bookmark.query.filter_by(post_id=post_id, user_id=current_user.id).first()

    if existing:
        db.session.delete(existing)
        post.bookmark_count = max(0, post.bookmark_count - 1)
        db.session.commit()
        return jsonify({'bookmarked': False, 'count': post.bookmark_count})
    else:
        bm = Bookmark(post_id=post_id, user_id=current_user.id)
        db.session.add(bm)
        post.bookmark_count += 1
        db.session.commit()
        return jsonify({'bookmarked': True, 'count': post.bookmark_count})


# ── Reposts ──────────────────────────────────────────

@api_bp.route('/posts/<int:post_id>/repost', methods=['POST'])
@login_required
def toggle_repost(post_id):
    from models.social import Repost
    post = Post.query.get_or_404(post_id)
    comment = request.form.get('comment', '').strip()
    existing = Repost.query.filter_by(post_id=post_id, user_id=current_user.id).first()

    if existing and not comment:
        db.session.delete(existing)
        post.repost_count = max(0, post.repost_count - 1)
        db.session.commit()
        return jsonify({'reposted': False, 'count': post.repost_count})
    else:
        if existing:
            existing.comment = comment
        else:
            rp = Repost(post_id=post_id, user_id=current_user.id, comment=comment)
            db.session.add(rp)
            post.repost_count += 1
        db.session.commit()

        if post.author_id != current_user.id:
            notif = Notification(
                user_id=post.author_id,
                type='repost',
                message=f'@{current_user.username} reposted your post "{post.title[:50]}"',
                link=f'/post/{post.id}',
            )
            db.session.add(notif)
            db.session.commit()

        return jsonify({'reposted': True, 'count': post.repost_count})


# ── Live Instant Search ──────────────────────────────

@api_bp.route('/search/live')
def live_search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'users': [], 'posts': [], 'tags': []})

    from models.user import User
    from models.post import Tag

    # Find matching users
    users = User.query.filter(
        (User.username.ilike(f'%{q}%')) | (User.display_name.ilike(f'%{q}%'))
    ).limit(5).all()

    # Find matching posts
    posts = Post.query.filter(
        Post.is_removed == False,
        (Post.title.ilike(f'%{q}%')) | (Post.content.ilike(f'%{q}%')) | (Post.code_snippet.ilike(f'%{q}%'))
    ).order_by(Post.created_at.desc()).limit(5).all()

    # Find matching tags
    tags = Tag.query.filter(Tag.name.ilike(f'%{q}%')).limit(5).all()

    return jsonify({
        'users': [{'username': u.username, 'display_name': u.display_name, 'avatar_url': u.avatar_url} for u in users],
        'posts': [{'id': p.id, 'title': p.title, 'author': p.author.username, 'post_type': p.post_type} for p in posts],
        'tags': [{'name': t.name} for t in tags]
    })


# ── Followers / Following Modals Data ────────────────

@api_bp.route('/users/<int:user_id>/followers')
def get_followers(user_id):
    from models.user import User
    user = User.query.get_or_404(user_id)
    followers_rel = Follow.query.filter_by(following_id=user.id).all()
    follower_ids = [f.follower_id for f in followers_rel]
    followers = User.query.filter(User.id.in_(follower_ids)).all() if follower_ids else []

    current_user_following = set()
    if current_user.is_authenticated:
        current_user_following = set(
            f.following_id for f in Follow.query.filter_by(follower_id=current_user.id).all()
        )

    return jsonify([{
        'id': u.id,
        'username': u.username,
        'display_name': u.display_name,
        'avatar_url': u.avatar_url,
        'bio': u.bio[:100],
        'is_following': u.id in current_user_following,
        'is_self': current_user.is_authenticated and u.id == current_user.id
    } for u in followers])


@api_bp.route('/users/<int:user_id>/following')
def get_following(user_id):
    from models.user import User
    user = User.query.get_or_404(user_id)
    following_rel = Follow.query.filter_by(follower_id=user.id).all()
    following_ids = [f.following_id for f in following_rel]
    following_users = User.query.filter(User.id.in_(following_ids)).all() if following_ids else []

    current_user_following = set()
    if current_user.is_authenticated:
        current_user_following = set(
            f.following_id for f in Follow.query.filter_by(follower_id=current_user.id).all()
        )

    return jsonify([{
        'id': u.id,
        'username': u.username,
        'display_name': u.display_name,
        'avatar_url': u.avatar_url,
        'bio': u.bio[:100],
        'is_following': u.id in current_user_following,
        'is_self': current_user.is_authenticated and u.id == current_user.id
    } for u in following_users])


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

