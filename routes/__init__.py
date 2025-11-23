from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
public_bp = Blueprint('public', __name__)
autor_bp = Blueprint('autor', __name__)  
editor_bp = Blueprint('editor', __name__)
admin_bp = Blueprint('admin', __name__)  


from routes import auth, public, autor, editor, admin