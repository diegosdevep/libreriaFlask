from flask import render_template, request
from routes import public_bp
import requests

@public_bp.route('/')
def index():
    return render_template('index.html')

@public_bp.route('/catalogo')
def catalogo():
    user_query = request.args.get('q', '')
    query = user_query if user_query else 'bestseller'
    
    try:
        response = requests.get(
            'https://openlibrary.org/search.json',
            params={'q': query, 'limit': 12}
        )
        data = response.json()
        libros = data.get('docs', [])
    except:
        libros = []
    
    return render_template('catalogo.html', libros=libros, query=user_query)