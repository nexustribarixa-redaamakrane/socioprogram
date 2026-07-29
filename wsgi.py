import os
import sys

# Add project directory to python path for PythonAnywhere WSGI handler
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import create_app

# WSGI application object expected by PythonAnywhere
application = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == '__main__':
    try:
        from waitress import serve
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', 5000))
        print(f"Serving production WSGI app (Waitress) on http://{host}:{port}")
        serve(application, host=host, port=port)
    except ImportError:
        application.run()
