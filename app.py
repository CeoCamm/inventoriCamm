from flask import *
from werkzeug.security import *
from pymongo import *
import os
from bson.objectid import *
from bson import json_util

app = Flask(__name__)
app.secret_key = 'QQPWOEIRUTY'

# CONEXION MONDONGO
client = MongoClient("mongodb+srv://crsmj11:hola1234@cluster0.44uo3mj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['my_inventory_app']
users_collection = db['users']
products_collection = db['products']
# PAGINA PRINCIPAL (WEB)
@app.route('/')
def home():
    return render_template('index.html')

# REGISTRARSE (WEB)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = users_collection.find_one({"username": username})

        if existing_user:
            flash('El Nombre de Usuario ya está en uso. Por favor elija otro', 'danger')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash('Registro exitoso. Ahora puedes iniciar sesión descargando la aplicación.', 'success')
        return redirect(url_for('register'))
    return render_template('register.html')

# LOGIN (APLICACION)
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = users_collection.find_one({"username": username})
    if user and check_password_hash(user['password'], password):
        return jsonify({"status": "success", "user_id": str(user['_id'])}), 200
    return jsonify({"status": "error", "message": "Usuario o contraseña incorrectos"}), 401
# APLICACION
@app.route('/api/dashboard/<user_id>', methods=['GET'])
def api_dashboard(user_id):
    products = list(products_collection.find({"user_id": user_id}))

    for product in products:
        product['_id'] = str(product['_id'])  

    return jsonify(products), 200
# AÑADIR PRODUCTO (APLICAION)
@app.route('/api/add_product', methods=['POST'])
def api_add_product():
    try:
        data = request.json
        name = data.get('name')
        category = data.get('category')
        stock = data.get('stock')
        price = data.get('price')
        user_id = data.get('user_id')

        app.logger.info(f"Data received: {data}")
# VERIFICACION DE EXISTENCIA DE LOS ITEMS
        if not (name and category and stock is not None and price is not None and user_id):
            return jsonify({"status": "error", "message": "Campos incompletos"}), 400

        products_collection.insert_one({"name": name, "category": category, "stock": stock, "price": price, "user_id": user_id})
        return jsonify({"status": "success"}), 200

    except Exception as e:
        app.logger.error(f"Error al agregar producto: {str(e)}")
        return jsonify({"status": "error", "message": "Error al procesar la solicitud"}), 500

# EDITAR PRODUCTO (APLICACION)
@app.route('/api/edit_product', methods=['POST'])
def api_edit_product():
    data = request.json
    product_id = data.get('product_id')
    name = data.get('name')
    category = data.get('category')
    stock = data.get('stock')
    price = data.get('price')
    products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": {"name": name, "category": category, "stock": stock, "price": price}})
    return jsonify({"status": "success"}), 200
# ELIMINAR PRODUCTO (APLICACION)
@app.route('/api/delete_product', methods=['POST'])
def api_delete_product():
    data = request.json
    product_id = data.get('product_id')
    products_collection.delete_one({"_id": ObjectId(product_id)})
    return jsonify({"status": "success"}), 200
# BUSCAR PRODUCTO (APLICACION)
@app.route('/api/search', methods=['GET'])
def api_search():
    category = request.args.get('category')
    user_id = request.args.get('user_id')
    products = products_collection.find({"user_id": user_id, "category": category})
    products_list = [{"name": product["name"], "category": product["category"], "_id": str(product["_id"])} for product in products]
    return jsonify(products_list), 200
# ACTUALIZAR PRODUCTO (APLICACION)
@app.route('/api/update_product', methods=['POST'])
def update_product():
    data = request.json
    product_id = data.get('product_id')
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    stock = data.get('stock')

    if not product_id or not name or not category or not price:
        return jsonify({"message": "Faltan datos requeridos"}), 400

    try:
        result = db.products.find_one_and_update(
            {"_id": ObjectId(product_id)},
            {"$set": {"name": name, "category": category, "price": price, "stock": stock}},
            return_document=ReturnDocument.AFTER
        )

        if result:
            return jsonify({"message": "Producto actualizado correctamente"}), 200
        else:
            return jsonify({"message": "Producto no encontrado"}), 404

    except Exception as e:
        return jsonify({"message": str(e)}), 500
# DESCARGAR APLICACION (WEB)    
@app.route('/download-app', methods=['GET'])
def download_app():
    try:
        return send_file('D:\INACAP\CAMM 3.0\CAMM\CAMM.rar', as_attachment=True)
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run(debug=True)
