from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import Warehouse, Sale, Product, Inventory

alert_bp = Blueprint('alert', __name__, url_prefix='/api/companies')

@alert_bp.route('/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    cutoff = datetime.utcnow() - timedelta(days=30)
    alerts = []

    warehouses = Warehouse.query.filter_by(company_id=company_id).all()
    for wh in warehouses:
        sales = Sale.query.filter(Sale.warehouse_id == wh.id, Sale.sale_date >= cutoff).all()
        recent_product_ids = set(s.product_id for s in sales)

        for pid in recent_product_ids:
            product = Product.query.get(pid)
            inventory = Inventory.query.filter_by(product_id=pid, warehouse_id=wh.id).first()

            if inventory and inventory.quantity < product.threshold:
                recent_sales = [s for s in sales if s.product_id == pid]
                daily_avg = sum(s.quantity for s in recent_sales) / 30 if recent_sales else 0
                days_until_stockout = int(inventory.quantity / daily_avg) if daily_avg else None
                supplier = product.suppliers[0] if product.suppliers else None

                alerts.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "sku": product.sku,
                    "warehouse_id": wh.id,
                    "warehouse_name": wh.name,
                    "current_stock": inventory.quantity,
                    "threshold": product.threshold,
                    "days_until_stockout": days_until_stockout,
                    "supplier": {
                        "id": supplier.id,
                        "name": supplier.name,
                        "contact_email": supplier.contact_email
                    } if supplier else None
                })

    return jsonify({"alerts": alerts, "total_alerts": len(alerts)})