from config import sdk
from flask import Blueprint, request, jsonify, abort
from models import db, User, Product, Order, OrderDetail

api = Blueprint('api', __name__)

@api.route('/create-preference', methods=['POST'])
def create_preference():
    try:
        data = request.get_json()
        total = 0

        order = Order()
        order.client_id = data.get('user_id')
        order.status = "pending"

        for prod in data.get("items"):
            # calculo indivial por producto
            t = float(prod["quantity"] * prod["price"])

            ordD = OrderDetail()
            ordD.product_id = prod["product_id"]
            ordD.quantity = prod["quantity"]
            ordD.price = prod["price"]
            ordD.total = t

            # agregar detalle a la orden 
            order.order_details.append(ordD)

            # el total de la orden
            total += t

        order.total = total
        order.save()

        external_reference = order.id

        items = [
            {
                "title": "Pago de Orden",
                "quantity": int(1),
                "unit_price": int(total),
                "currency_id": "CLP"
            }
        ]
        back_urls = {
            "success": "http://localhost:5173/success",
            "failure": "http://localhost:5173/failure",
            "pending": "http://localhost:5173/pending"
        }
        auto_return = "approved"

        preference_data = {
            "items": items,
            "back_urls": back_urls,
            "auto_return": auto_return,
            "external_reference": external_reference
        }

        # crear la preferencia
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        updateOrder = Order.query.get(order.id)
        updateOrder.preference = preference["id"]
        updateOrder.update()

    
        return jsonify({
            "id": preference["id"],
            "init_point": preference["init_point"],
            #"preference_data": preference_data,
            "message": "preferencia de pago creada exitosamente"
        })

    except Exception as e:
        abort(500)

@api.route('/update-order', methods=['POST'])
def update_order():

    try:

        data = request.get_json()

        order = Order.query.get(int(data.get('external_reference')))

        order.status = data.get('status')
        order.reference_id = data.get('payment_id')
        order.payment_method = data.get('payment_type')
        order.update()

        return jsonify({
            "status": "success" if data.get('status') == "approved" else "danger",
            "message": "pago recibido con exito" if data.get('status') == "approved" else "el pago ha sido rechazado",
        })
    
    except Exception as e:
        abort(500)