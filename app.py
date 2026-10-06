from flask import Flask, jsonify, request

app = Flask(__name__)

inventory = []      # simulated database
_next_id = 1
ALLOWED = {"name", "brand", "price", "quantity", "barcode",
           "ingredients", "nutriscore", "nova_group"}


def reset_inventory():
    global _next_id
    inventory.clear()
    _next_id = 1


def find_item(item_id):
    return next((i for i in inventory if i["id"] == item_id), None)


def validate(data, partial=False):
    if not partial and not data.get("name"):
        return "name is required"
    if "price" in data and (not isinstance(data["price"], (int, float)) or data["price"] < 0):
        return "price must be a non-negative number"
    if "quantity" in data and (not isinstance(data["quantity"], int) or data["quantity"] < 0):
        return "quantity must be a non-negative integer"
    return None


def create_item(data):
    global _next_id
    item = {
        "id": _next_id,
        "name": data["name"],
        "brand": data.get("brand", ""),
        "price": data.get("price", 0),
        "quantity": data.get("quantity", 0),
        "barcode": data.get("barcode"),
        "ingredients": data.get("ingredients", ""),
        "nutriscore": data.get("nutriscore"),
        "nova_group": data.get("nova_group"),
    }
    inventory.append(item)
    _next_id += 1
    return item


@app.get("/inventory")
def list_items():
    return jsonify(inventory), 200


@app.get("/inventory/<int:item_id>")
def get_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify(error="Item not found"), 404
    return jsonify(item), 200


@app.post("/inventory")
def add_item():
    data = request.get_json(silent=True) or {}
    error = validate(data)
    if error:
        return jsonify(error=error), 400
    return jsonify(create_item(data)), 201


@app.patch("/inventory/<int:item_id>")
def update_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify(error="Item not found"), 404
    data = request.get_json(silent=True) or {}
    data = {k: v for k, v in data.items() if k in ALLOWED}
    if not data:
        return jsonify(error="No valid fields to update"), 400
    error = validate(data, partial=True)
    if error:
        return jsonify(error=error), 400
    item.update(data)
    return jsonify(item), 200


@app.delete("/inventory/<int:item_id>")
def delete_item(item_id):
    item = find_item(item_id)
    if not item:
        return jsonify(error="Item not found"), 404
    inventory.remove(item)
    return jsonify(message="Item deleted"), 200


if __name__ == "__main__":
    app.run(debug=True)