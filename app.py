from flask import Flask, request, jsonify, render_template, session
from models import db, BlogPost, User
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Změňte na bezpečný klíč

# Inicializace databáze
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/api/register', methods=['POST'])
def register_user():
    """Registrace nového uživatele."""
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400

    new_user = User(username=data['username'], password=generate_password_hash(data['password']))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/api/login', methods=['POST'])
def login_user():
    """Přihlášení uživatele."""
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and check_password_hash(user.password, data.get('password')):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful", "user_id": user.id}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@app.route('/api/logout', methods=['POST'])
def logout_user():
    """Odhlášení uživatele."""
    session.pop('user_id', None)
    return jsonify({"message": "Logout successful"}), 200


@app.route('/api/blog', methods=['POST'])
def create_blog_post():
    """Vytvoření nového blogového příspěvku."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data or 'content' not in data:
        return jsonify({"error": "Missing content"}), 400

    new_post = BlogPost(content=data['content'], author_id=session['user_id'], created_at=datetime.utcnow())
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"id": new_post.id}), 201


@app.route('/api/blog', methods=['GET'])
def get_blog_posts():
    """Získání všech blogových příspěvků."""
    posts = BlogPost.query.all()
    return jsonify([post.to_dict() for post in posts])


@app.route('/api/blog/user/<int:user_id>', methods=['GET'])
def get_user_blog_posts(user_id):
    """Získání blogových příspěvků konkrétního uživatele."""
    if 'user_id' not in session or session['user_id'] != user_id:
        return jsonify({"error": "Unauthorized"}), 401

    posts = BlogPost.query.filter_by(author_id=user_id).all()
    return jsonify([post.to_dict() for post in posts])


@app.route('/api/blog/<int:blog_id>', methods=['DELETE'])
def delete_blog_post(blog_id):
    """Smazání blogového příspěvku."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    post = BlogPost.query.get(blog_id)
    if post and post.author_id == session['user_id']:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Blog post deleted"}), 200
    return jsonify({"error": "Blog post not found or unauthorized"}), 404


@app.route('/api/blog/<int:blog_id>', methods=['PATCH'])
def update_blog_post(blog_id):
    """Aktualizace blogového příspěvku."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    if not data or 'content' not in data:
        return jsonify({"error": "Missing content"}), 400

    post = BlogPost.query.get(blog_id)
    if post and post.author_id == session['user_id']:
        post.content = data['content']
        db.session.commit()
        return jsonify({"message": "Blog post updated"}), 200
    return jsonify({"error": "Blog post not found or unauthorized"}), 404


@app.route('/api/about', methods=['GET'])
def api_about():
    """Zobrazení dokumentace k API."""
    api_info = {
        "description": "Toto API poskytuje možnosti pro správu blogových příspěvků.",
        "endpoints": {
            "/api/register": {
                "method": "POST",
                "description": "Registrace nového uživatele.",
                "request_format": {
                    "username": "string",
                    "password": "string"
                },
                "response_format": {
                    "message": "string"
                }
            },
            "/api/login": {
                "method": "POST",
                "description": "Přihlášení uživatele.",
                "request_format": {
                    "username": "string",
                    "password": "string"
                },
                "response_format": {
                    "message": "string",
                    "user_id": "integer"
                }
            },
            "/api/logout": {
                "method": "POST",
                "description": "Odhlášení uživatele.",
                "response_format": {
                    "message": "string"
                }
            },
            "/api/blog": {
                "method": "POST",
                "description": "Vytvoření nového blogového příspěvku.",
                "request_format": {
                    "content": "string"
                },
                "response_format": {
                    "id": "integer"
                }
            },
            "/api/blog": {
                "method": "GET",
                "description": "Získání všech blogových příspěvků.",
                "response_format": [
                    {
                        "id": "integer",
                        "content": "string",
                        "author_id": "integer",
                        "created_at": "string (ISO 8601)"
                    }
                ]
            },
            "/api/blog/user/<int:user_id>": {
                "method": "GET",
                "description": "Získání blogových příspěvků konkrétního uživatele.",
                "response_format": [
                    {
                        "id": "integer",
                        "content": "string",
                        "created_at": "string (ISO 8601)"
                    }
                ]
            },
            "/api/blog/<int:blog_id>": {
                "method": "DELETE",
                "description": "Smazání blogového příspěvku.",
                "response_format": {
                    "message": "string"
                }
            },
            "/api/blog/<int:blog_id>": {
                "method": "PATCH",
                "description": "Aktualizace blogového příspěvku.",
                "request_format": {
                    "content": "string"
                },
                "response_format": {
                    "message": "string"
                }
            },
            "/api/about": {
                "method": "GET",
                "description": "Zobrazení dokumentace API.",
                "response_format": {
                    "description": "string",
                    "endpoints": "object"
                }
            }
        },
        "authorization": "Všechny endpointy kromě /api/register a /api/login vyžadují autentizaci pomocí HTTP Basic Auth."
    }
    return jsonify(api_info), 200


@app.route('/')
def index():
    """Hlavní stránka."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
