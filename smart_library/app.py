from flask import Flask, redirect, url_for
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.books import books_bp
from routes.scanner import scanner_bp
from routes.map_view import map_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(books_bp)
app.register_blueprint(scanner_bp)
app.register_blueprint(map_bp)


@app.route('/')
def home():
    return redirect(url_for('books.search'))   # home page goes to the search page


if __name__ == '__main__':
    app.run(debug=True)
