from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.post import Post
from models.moderation import Ban, Report, Rule
from models.notification import Notification

moderation_bp = Blueprint('moderation', __name__, url_prefix='/mod')


def mod_required(f):
    """Decorator to restrict access to moderators and admins."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_moderator:
            flash('Access denied. Moderator privileges required.', 'error')
            return redirect(url_for('feed.index'))
        return f(*args, **kwargs)
    return decorated


@moderation_bp.route('/')
@login_required
@mod_required
def dashboard():
    pending_reports = Report.query.filter_by(status='pending').order_by(
        Report.created_at.desc()
    ).limit(50).all()

    recent_bans = Ban.query.filter_by(is_active=True).order_by(
        Ban.created_at.desc()
    ).limit(20).all()

    stats = {
        'pending_reports': Report.query.filter_by(status='pending').count(),
        'total_bans_active': Ban.query.filter_by(is_active=True).count(),
        'total_users': User.query.count(),
        'total_posts': Post.query.filter_by(is_removed=False).count(),
    }

    return render_template('moderation/dashboard.html',
                           reports=pending_reports,
                           recent_bans=recent_bans,
                           stats=stats)


@moderation_bp.route('/rules')
def rules():
    """Public community rules page — visible to everyone."""
    all_rules = Rule.query.filter_by(is_active=True).order_by(Rule.order).all()
    return render_template('moderation/rules.html', rules=all_rules)


@moderation_bp.route('/bans')
def bans():
    """Public ban log — transparency."""
    page = request.args.get('page', 1, type=int)
    pagination = Ban.query.order_by(Ban.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('moderation/bans.html',
                           bans=pagination.items,
                           pagination=pagination)


@moderation_bp.route('/report/<int:report_id>/action', methods=['POST'])
@login_required
@mod_required
def action_report(report_id):
    report = Report.query.get_or_404(report_id)
    action = request.form.get('action')  # 'dismiss' | 'warn' | 'temp_ban' | 'perm_ban' | 'remove_post'
    notes = request.form.get('notes', '').strip()
    duration_days = request.form.get('duration_days', 7, type=int)

    report.status = 'actioned' if action != 'dismiss' else 'dismissed'
    report.reviewed_by_id = current_user.id
    report.review_notes = notes

    target_user = None
    if report.reported_user_id:
        target_user = User.query.get(report.reported_user_id)
    elif report.post_id:
        post = Post.query.get(report.post_id)
        if post:
            target_user = User.query.get(post.author_id)

    if action == 'remove_post' and report.post_id:
        post = Post.query.get(report.post_id)
        if post:
            post.is_removed = True
            post.removed_reason = notes or 'Removed by moderator.'
            if target_user:
                notif = Notification(
                    user_id=target_user.id,
                    type='mod_action',
                    message=f'Your post "{post.title[:50]}" was removed. Reason: {post.removed_reason}',
                    link=f'/mod/rules',
                )
                db.session.add(notif)

    elif action == 'warn' and target_user:
        notif = Notification(
            user_id=target_user.id,
            type='warning',
            message=f'⚠️ Warning from moderators: {notes or "Please review the community rules."}',
            link='/mod/rules',
        )
        db.session.add(notif)

    elif action == 'temp_ban' and target_user:
        expires = datetime.now(timezone.utc) + timedelta(days=duration_days)
        ban = Ban(
            user_id=target_user.id,
            banned_by_id=current_user.id,
            reason=notes or 'Rule violation.',
            ban_type='temporary',
            duration_days=duration_days,
            expires_at=expires,
        )
        target_user.is_banned = True
        target_user.ban_reason = ban.reason
        target_user.ban_until = expires
        db.session.add(ban)

        notif = Notification(
            user_id=target_user.id,
            type='mod_action',
            message=f'You have been temporarily banned for {duration_days} days. Reason: {ban.reason}',
            link='/mod/rules',
        )
        db.session.add(notif)

    elif action == 'perm_ban' and target_user:
        ban = Ban(
            user_id=target_user.id,
            banned_by_id=current_user.id,
            reason=notes or 'Severe rule violation.',
            ban_type='permanent',
        )
        target_user.is_banned = True
        target_user.ban_reason = ban.reason
        target_user.ban_until = None
        db.session.add(ban)

        notif = Notification(
            user_id=target_user.id,
            type='mod_action',
            message=f'You have been permanently banned. Reason: {ban.reason}',
            link='/mod/rules',
        )
        db.session.add(notif)

    db.session.commit()
    flash(f'Report #{report_id} — action taken: {action}', 'success')
    return redirect(url_for('moderation.dashboard'))


@moderation_bp.route('/ban/<int:ban_id>/lift', methods=['POST'])
@login_required
@mod_required
def lift_ban(ban_id):
    ban = Ban.query.get_or_404(ban_id)
    ban.is_active = False

    user = User.query.get(ban.user_id)
    if user:
        # Check if there are other active bans
        other_active = Ban.query.filter(
            Ban.user_id == user.id, Ban.id != ban.id, Ban.is_active == True
        ).first()
        if not other_active:
            user.is_banned = False
            user.ban_reason = ''
            user.ban_until = None

    db.session.commit()
    flash(f'Ban #{ban_id} has been lifted.', 'success')
    return redirect(url_for('moderation.dashboard'))
