from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from models import db
from models.notification import Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('NOTIFICATIONS_PER_PAGE', 30)

    pagination = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Notification.is_read.asc(),
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Mark all as read when viewing the page
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()

    return render_template('notifications/index.html',
                           notifications=pagination.items,
                           pagination=pagination)
