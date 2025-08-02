from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Global SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stockflow.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from .models import Company, Warehouse, Supplier, Product, SupplierProduct, Inventory, InventoryLog, Sale
        from .routes.products import product_bp
        from .routes.alerts import alert_bp
        db.create_all()

        # Register blueprints
        app.register_blueprint(product_bp)
        app.register_blueprint(alert_bp)

    return app