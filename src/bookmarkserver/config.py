import os
import secrets
if os.environ.get("FLASK_ENV",'').lower() == 'development':
    DATABASE_URL = os.environ.get("DATABASE_URL", 'sqlite:///:memory:')
    DEBUG=True
    EXPLAIN_TEMPLATE_LOADING = os.environ.get('EXPLAIN_TEMPLATE_RELOADING')
else:
    DATABASE_URL = os.environ.get("DATABASE_URL", 'sqlite:///bookmarks.db')
ENV = os.environ.get("ENV", 'production')
SECRET_KEY = secrets.token_hex(64)
PORT=int(os.environ.get("PORT",80))
SQLALCHEMY_DATABASE_URI = DATABASE_URL
CONNECTION_TIMEOUT_LIMIT = int(os.environ.get('CONNECTION_TIMEOUT_LIMIT', 15))