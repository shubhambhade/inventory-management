from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from app import db
from app.models import Product, Inventory

product_bp = Blueprint('product', __name__, url_prefix='/api/products')

@product_bp.route('', methods=['POST'])
def create_product():
    data = request.json
    required_fields = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if Product.query.filter_by(sku=data['sku']).first():
        return jsonify({"error": "SKU already exists"}), 409

    try:
        with db.session.begin_nested():
            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=Decimal(str(data['price'])),
                threshold=data.get('threshold', 10)
            )
            db.session.add(product)
            db.session.flush()

            inventory = Inventory(
                product_id=product.id,
                warehouse_id=data['warehouse_id'],
                quantity=data['initial_quantity']
            )
            db.session.add(inventory)

        db.session.commit()
        return jsonify({"message": "Product created", "product_id": product.id}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database error"}), 500