from flask import Flask, render_template, redirect, url_for, flash, session
from config import Config
from database.connection import init_db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.library import library_bp
from routes.store import store_bp
from routes.tickets import tickets_bp
from routes.admin import admin_bp
from routes.reports import reports_bp
import os

app = Flask(__name__)
app.config.from_object(Config)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(library_bp)
app.register_blueprint(store_bp)
app.register_blueprint(tickets_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(reports_bp)

# Global context processor to make cart size available everywhere in templates
@app.context_processor
def inject_cart_size():
    cart = session.get('cart', {})
    return {'cart_size': len(cart)}

# Error Handlers for a professional experience
@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', page_header="Page Not Found")

@app.errorhandler(500)
def server_error(e):
    return "Internal Server Error. Please contact support.", 500

# Initialize database schema and inject seeds on app startup
with app.app_context():
    # Make sure static uploads folder exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    init_db()

if __name__ == '__main__':
    # Run dev server on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
