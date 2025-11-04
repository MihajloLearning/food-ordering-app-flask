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
            result.append({
                'id': o.id,
                'restaurant_name': o.restaurant.name,
                'orderer_name': o.orderer_name,
                'created_at': o.created_at.isoformat(),
                'items': [{'user_name': item.user_name, 'item_name': item.item_name} for item in o.order_items]
            })
        return jsonify(result)

    @app.route('/api/orders', methods=['POST'])
    def place_order():
        data = request.get_json()
        new_order = Order(restaurant_id=data['restaurant_id'], orderer_name=data['orderer_name'])
        db.session.add(new_order)
        db.session.commit()

        for item in data['items']:
            order_item = OrderItem(order_id=new_order.id, user_name=item['user_name'], item_name=item['item_name'])
            db.session.add(order_item)
        
        db.session.commit()
        return jsonify({'id': new_order.id})