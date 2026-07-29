import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
from models import db

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Sign in to access this page.'
login_manager.login_message_category = 'info'

csrf = CSRFProtect()


def seed_rules():
    """Seed default community rules on first run."""
    from models.moderation import Rule
    if Rule.query.count() == 0:
        rules = [
            Rule(title='No off-topic content',
                 description='Posts must be about code, projects, tools, or engineering. No memes, politics, or lifestyle content.',
                 severity='warning', order=1),
            Rule(title='No advertisements or self-promotion spam',
                 description='Showcasing your project is fine. Spamming it in every thread is not.',
                 severity='temp_ban', order=2),
            Rule(title='No harassment, personal attacks, or toxicity',
                 description='Criticize code, not people. "Your architecture has X flaw" is fine — "You\'re a bad developer" is not.',
                 severity='perm_ban', order=3),
            Rule(title='No AI-generated spam',
                 description='Posts must show genuine human effort. Copy-pasting ChatGPT output as your "project" is not a contribution.',
                 severity='temp_ban', order=4),
            Rule(title='No clickbait titles',
                 description='Use clear, descriptive titles. "You won\'t BELIEVE this hack" is not acceptable.',
                 severity='warning', order=5),
            Rule(title='No malicious code',
                 description='Sharing exploits, malware, or intentionally harmful code results in an instant permanent ban.',
                 severity='perm_ban', order=6),
            Rule(title='No impersonation',
                 description='Don\'t pretend to be another developer or claim others\' projects as yours.',
                 severity='perm_ban', order=7),
            Rule(title='Keep it constructive',
                 description='If reviewing someone\'s code, offer actionable feedback. "This sucks" is not constructive.',
                 severity='warning', order=8),
            Rule(title='No NSFW content',
                 description='This is a professional engineering platform. Keep it clean.',
                 severity='perm_ban', order=9),
            Rule(title='Respect open source licenses',
                 description='When showcasing code, credit original authors and respect licenses.',
                 severity='warning', order=10),
        ]
        db.session.add_all(rules)
        db.session.commit()


def migrate_db():
    """Ensure missing columns are added to existing SQLite database tables."""
    with db.engine.connect() as conn:
        # Check users table columns
        result = conn.execute(db.text("PRAGMA table_info(users)")).fetchall()
        user_cols = {row[1] for row in result}
        for col_name, col_type in [
            ('banner_path', 'VARCHAR(512) DEFAULT ""'),
            ('tech_stack', 'VARCHAR(256) DEFAULT ""'),
            ('website', 'VARCHAR(256) DEFAULT ""'),
            ('location', 'VARCHAR(128) DEFAULT ""')
        ]:
            if col_name not in user_cols:
                conn.execute(db.text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                conn.commit()

        # Check posts table columns
        result = conn.execute(db.text("PRAGMA table_info(posts)")).fetchall()
        post_cols = {row[1] for row in result}
        for col_name, col_type in [
            ('bookmark_count', 'INTEGER DEFAULT 0'),
            ('repost_count', 'INTEGER DEFAULT 0')
        ]:
            if col_name not in post_cols:
                conn.execute(db.text(f"ALTER TABLE posts ADD COLUMN {col_name} {col_type}"))
                conn.commit()


def create_app(config_name=None):
    """Application factory."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader for Flask-Login
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Create upload directories
    upload_base = app.config.get('UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'uploads'))
    for subdir in ('avatars', 'posts', 'banners'):
        path = os.path.join(upload_base, subdir)
        os.makedirs(path, exist_ok=True)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.feed import feed_bp
    from routes.posts import posts_bp
    from routes.profile import profile_bp
    from routes.search import search_bp
    from routes.notifications import notifications_bp
    from routes.moderation import moderation_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(feed_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(moderation_bp)
    app.register_blueprint(api_bp)

    # Context processor — inject globals into all templates
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        unread_count = 0
        if current_user.is_authenticated:
            from models.notification import Notification
            unread_count = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return {
            'unread_notification_count': unread_count,
            'google_oauth_enabled': bool(app.config.get('GOOGLE_CLIENT_ID')),
            'github_oauth_enabled': bool(app.config.get('GITHUB_CLIENT_ID')),
            'reddit_oauth_enabled': bool(app.config.get('REDDIT_CLIENT_ID')),
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Create database tables, run column migrations and seed rules
    with app.app_context():
        db.create_all()
        migrate_db()
        seed_rules()

    return app


# Entry point
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
