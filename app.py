from flask import Flask, request, redirect, url_for
from flask_restful import Api, Resource
from models import db, Product

app = Flask(__name__)

# SQLite config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
api = Api(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return redirect(url_for("products"))

def validate_price(price):
    try:
        price = float(price)
        return price > 0
    except (ValueError, TypeError):
        return False

class ProductListResource(Resource):
    def get(self):
        products = Product.query.all()
        return {"status": "success", "products": [p.to_dict() for p in products]}, 200

    def post(self):
        data = request.get_json()

        if not data:
            return {"status": "error", "message": "Missing JSON body"}, 400

        name = data.get("name")
        price = data.get("price")
        in_stock = data.get("in_stock", True)

        if not name or price is None:
            return {"status": "error", "message": "Name and Price are required"}, 400

        if not validate_price(price):
            return {"status": "error", "message": "Price must be a number > 0"}, 400

        new_product = Product(name=name, price=float(price), in_stock=bool(in_stock))
        db.session.add(new_product)
        db.session.commit()

        return {"status": "success", "product": new_product.to_dict()}, 201


class ProductResource(Resource):
    def get(self, id):
        product = Product.query.get_or_404(id)
        return {"status": "success", "product": product.to_dict()}, 200

    def put(self, id):
        product = Product.query.get_or_404(id)
        data = request.get_json()

        if "name" in data:
            product.name = data["name"]
        if "price" in data:
            if not validate_price(data["price"]):
                return {"status": "error", "message": "Price must be a number > 0"}, 400
            product.price = float(data["price"])
        if "in_stock" in data:
            product.in_stock = bool(data["in_stock"])

        db.session.commit()
        return {"status": "success", "product": product.to_dict()}, 200

    def delete(self, id):
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return {"status": "success", "message": "Product deleted"}, 200

# Register endpoints
api.add_resource(ProductListResource, "/products", endpoint="products")
api.add_resource(ProductResource, "/products/<int:id>", endpoint="product")

if __name__ == "__main__":
    app.run(debug=False)

