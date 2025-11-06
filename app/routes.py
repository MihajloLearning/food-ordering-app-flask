from flask import request, jsonify, render_template
from app import db
from app.models import Restaurant, MenuItem, Order, OrderItem

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    # Restaurants
    @app.route('/api/restaurants', methods=['GET'])
    def get_restaurants():
        restaurants = Restaurant.query.all()
        return jsonify([{'id': r.id, 'name': r.name} for r in restaurants])

    @app.route('/api/restaurants', methods=['POST'])
    def add_restaurant():
        data = request.get_json()
        new_restaurant = Restaurant(name=data['name'])
        db.session.add(new_restaurant)
        db.session.commit()
        return jsonify({'id': new_restaurant.id, 'name': new_restaurant.name})

    @app.route('/api/restaurants/<int:id>', methods=['PUT'])
    def update_restaurant(id):
        restaurant = Restaurant.query.get_or_404(id)
        data = request.get_json()
        restaurant.name = data.get('name', restaurant.name)
        db.session.commit()
        return jsonify({'id': restaurant.id, 'name': restaurant.name})

    @app.route('/api/restaurants/<int:id>', methods=['DELETE'])
    def delete_restaurant(id):
        restaurant = Restaurant.query.get_or_404(id)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

    # Menu
    @app.route('/api/restaurants/<int:id>/menu', methods=['GET'])
    def get_menu(id):
        menu_items = MenuItem.query.filter_by(restaurant_id=id).all()
        return jsonify([{'id': item.id, 'name': item.name, 'price': str(item.price)} for item in menu_items])

    @app.route('/api/restaurants/<int:id>/menu', methods=['POST'])
    def add_menu_item(id):
        data = request.get_json()
        new_item = MenuItem(restaurant_id=id, name=data['name'], price=data['price'])
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'id': new_item.id, 'name': new_item.name, 'price': str(new_item.price)})

    @app.route('/api/menu/<int:id>', methods=['PUT'])
    def update_menu_item(id):
        item = MenuItem.query.get_or_404(id)
        data = request.get_json()
        item.name = data.get('name', item.name)
        item.price = data.get('price', item.price)
        db.session.commit()
        return jsonify({'id': item.id, 'name': item.name, 'price': str(item.price)})

    @app.route('/api/menu/<int:id>', methods=['DELETE'])
    def delete_menu_item(id):
        item = MenuItem.query.get(id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

    # Orders
    @app.route('/api/orders', methods=['GET'])
    def get_orders():
        orders = Order.query.order_by(Order.created_at.desc()).all()
        result = []
        for o in orders:
            if o.status == 'locked' or o.order_items:
                result.append({
                    'id': o.id,
                    'restaurant_name': o.restaurant.name,
                    'orderer_name': o.orderer_name,
                    'created_at': o.created_at.isoformat(),
                    'status': o.status,
                    'items': [{'user_name': item.user_name, 'item_name': item.item_name, 'id': item.id, 'notes': item.notes, 'price': str(item.price)} for item in o.order_items]
                })
        return jsonify(result)

    @app.route('/api/restaurants/<int:restaurant_id>/open-order', methods=['GET'])
    def get_or_create_open_order(restaurant_id):
        open_order = Order.query.filter_by(restaurant_id=restaurant_id, status='open').first()
        if not open_order:
            # Create a placeholder open order if none exists
            open_order = Order(restaurant_id=restaurant_id, orderer_name='Undecided', status='open')
            db.session.add(open_order)
            db.session.commit()
        
        return jsonify({
            'id': open_order.id,
            'restaurant_id': open_order.restaurant_id,
            'orderer_name': open_order.orderer_name,
            'created_at': open_order.created_at.isoformat(),
            'status': open_order.status,
            'items': [{'user_name': item.user_name, 'item_name': item.item_name, 'id': item.id, 'notes': item.notes, 'price': str(item.price)} for item in open_order.order_items]
        })

    @app.route('/api/orders/<int:order_id>/items', methods=['POST'])
    def add_item_to_open_order(order_id):
        order = Order.query.get_or_404(order_id)
        if order.status == 'locked':
            return jsonify({'error': 'Order is locked and cannot be modified.'}), 403

        data = request.get_json()
        new_item = OrderItem(order_id=order_id, user_name=data['user_name'], item_name=data['item_name'], notes=data.get('notes'), price=data['price'])
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'id': new_item.id, 'user_name': new_item.user_name, 'item_name': new_item.item_name, 'notes': new_item.notes, 'price': str(new_item.price)})

    @app.route('/api/order-items/<int:item_id>', methods=['PUT'])
    def update_order_item(item_id):
        order_item = OrderItem.query.get_or_404(item_id)
        if order_item.order.status == 'locked':
            return jsonify({'error': 'Order is locked and cannot be modified.'}), 403

        data = request.get_json()
        order_item.user_name = data.get('user_name', order_item.user_name)
        order_item.item_name = data.get('item_name', order_item.item_name)
        order_item.notes = data.get('notes', order_item.notes)
        order_item.price = data.get('price', order_item.price)
        db.session.commit()
        return jsonify({'id': order_item.id, 'user_name': order_item.user_name, 'item_name': order_item.item_name, 'notes': order_item.notes, 'price': str(order_item.price)})

    @app.route('/api/order-items/<int:item_id>', methods=['DELETE'])
    def delete_order_item(item_id):
        order_item = OrderItem.query.get_or_404(item_id)
        if order_item.order.status == 'locked':
            return jsonify({'error': 'Order is locked and cannot be modified.'}), 403

        db.session.delete(order_item)
        db.session.commit()
        return '', 204

    @app.route('/api/orders/<int:order_id>/lock', methods=['POST'])
    def lock_order(order_id):
        order = Order.query.get_or_404(order_id)
        order.status = 'locked'
        db.session.commit()
        return jsonify({'id': order.id, 'status': order.status})

    @app.route('/api/orders/<int:order_id>/orderer', methods=['PUT'])
    def update_orderer(order_id):
        order = Order.query.get_or_404(order_id)
        if order.status == 'locked':
            return jsonify({'error': 'Order is locked and orderer cannot be changed.'}), 403
        
        data = request.get_json()
        new_orderer_name = data.get('orderer_name')
        if new_orderer_name:
            order.orderer_name = new_orderer_name
            db.session.commit()
            return jsonify({'id': order.id, 'orderer_name': order.orderer_name})
        return jsonify({'error': 'Orderer name not provided.'}), 400

    @app.route('/api/orders/<int:order_id>', methods=['DELETE'])
    def cancel_order(order_id):
        order = Order.query.get_or_404(order_id)
        if order.status == 'locked':
            return jsonify({'error': 'Cannot cancel a locked order.'}), 403
        db.session.delete(order)
        db.session.commit()
        return '', 204
