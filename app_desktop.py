import sys
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("LoginWindow")
        self.setWindowTitle("Iniciar Sesión")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setObjectName("UsernameInput")
        self.username_input.setPlaceholderText("Nombre de Usuario")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setObjectName("PasswordInput")
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Iniciar Sesión", self)
        self.login_button.setObjectName("LoginButton")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        self.load_stylesheet("style.css")

    def load_stylesheet(self, filename):
        style_file = QFile(filename)
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stylesheet = style_file.readAll()
            style_file.close()
            self.setStyleSheet(bytes(stylesheet).decode("utf-8"))

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        response = requests.post('http://127.0.0.1:5000/api/login', json={"username": username, "password": password})

        if response.status_code == 200:
            data = response.json()
            self.user_id = data['user_id']
            self.dashboard_window = DashboardWindow(self.user_id)
            self.dashboard_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Usuario o contraseña incorrectos')

class DashboardWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.setObjectName("DashboardWindow")
        self.setWindowTitle("ORGANIZADOR CAMM")
        self.setGeometry(100, 100, 800, 600)
        self.user_id = user_id

        layout = QVBoxLayout()
#FILTROS

        filter_layout = QHBoxLayout()

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Nombre")
        self.filter_combo.addItem("Categoría")
        self.filter_combo.addItem("Precio")
        self.filter_combo.addItem("Stock")
        filter_layout.addWidget(self.filter_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar...")
        self.search_input.textChanged.connect(self.filter_products)
        filter_layout.addWidget(self.search_input)

        self.filter_button = QPushButton("Filtrar")
        self.filter_button.clicked.connect(self.filter_products)
        filter_layout.addWidget(self.filter_button)

        layout.addLayout(filter_layout)
#TABLA

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Categoría", "Precio", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Reiniciar")
        self.refresh_button.clicked.connect(self.load_products)
        button_layout.addWidget(self.refresh_button)

        self.add_button = QPushButton("Agregar Producto")
        self.add_button.clicked.connect(self.add_product)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Editar Producto")
        self.edit_button.clicked.connect(self.open_edit_window)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Eliminar Producto")
        self.delete_button.clicked.connect(self.open_delete_window)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.load_stylesheet("style.css")

        self.load_products()

    def load_stylesheet(self, filename):
        style_file = QFile(filename)
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stylesheet = style_file.readAll()
            style_file.close()
            self.setStyleSheet(bytes(stylesheet).decode("utf-8"))

    def load_products(self):
        response = requests.get(f'http://127.0.0.1:5000/api/dashboard/{self.user_id}')
        if response.status_code == 200:
            products = response.json()
            self.table.setRowCount(len(products))

            for row, product in enumerate(products):
                item_id = QTableWidgetItem(product['_id'])
                item_name = QTableWidgetItem(product['name'])
                item_category = QTableWidgetItem(product['category'])
                item_price = QTableWidgetItem(f"${product.get('price', 'N/A')}")
                item_stock = QTableWidgetItem(product.get('stock', 'N/A'))

                self.table.setItem(row, 0, item_id)
                self.table.setItem(row, 1, item_name)
                self.table.setItem(row, 2, item_category)
                self.table.setItem(row, 3, item_price)
                self.table.setItem(row, 4, item_stock)

    def update_table(self, products):
        self.table.setRowCount(len(products))

        for row, product in enumerate(products):
            item_id = QTableWidgetItem(product['_id'])
            item_name = QTableWidgetItem(product['name'])
            item_category = QTableWidgetItem(product['category'])
            item_price = QTableWidgetItem(f"${product.get('price', 'N/A')}")
            item_stock = QTableWidgetItem(product.get('stock', 'N/A'))

            self.table.setItem(row, 0, item_id)
            self.table.setItem(row, 1, item_name)
            self.table.setItem(row, 2, item_category)
            self.table.setItem(row, 3, item_price)    
            self.table.setItem(row, 4, item_stock)        

    def add_product(self):
        self.product_form_window = ProductFormWindow(self.user_id, "Agregar Producto")
        self.product_form_window.product_saved.connect(self.load_products)
        self.product_form_window.show()

    def open_edit_window(self):
        self.edit_window = SelectProductWindow(self.user_id, "Editar Producto")
        self.edit_window.product_selected.connect(self.edit_product)
        self.edit_window.show()

    def edit_product(self, product_id):
        self.product_form_window = ProductFormWindow(self.user_id, "Editar Producto", product_id)
        self.product_form_window.product_saved.connect(self.load_products)
        self.product_form_window.show()

    def open_delete_window(self):
        self.delete_window = SelectProductWindow(self.user_id, "Eliminar Producto")
        self.delete_window.product_selected.connect(self.delete_product)
        self.delete_window.show()

    def delete_product(self, product_id):
        response = requests.post('http://127.0.0.1:5000/api/delete_product', json={"product_id": product_id})
        if response.status_code == 200:
            self.load_products()
        else:
            QMessageBox.warning(self, 'Error', 'Error al eliminar el producto')

    def filter_products(self):
        filter_key = self.filter_combo.currentText().lower()
        search_term = self.search_input.text().strip().lower()

        response = requests.get(f'http://127.0.0.1:5000/api/dashboard/{self.user_id}')
        if response.status_code == 200:
            products = response.json()

            filtered_products = []
            for product in products:
                if filter_key == "nombre":
                    if search_term in product['name'].lower():
                        filtered_products.append(product)
                elif filter_key == "categoría":
                    if search_term in product['category'].lower():
                        filtered_products.append(product)
                elif filter_key == "precio":
                    if search_term in str(product.get('price', '')).lower():
                        filtered_products.append(product)
                elif filter_key == "stock":
                    if search_term in str(product.get('stock', '')).lower():
                        filtered_products.append(product)              

            self.update_table(filtered_products)
        else:
            QMessageBox.warning(self, 'Error', 'Error al cargar productos')

class SelectProductWindow(QWidget):
    product_selected = pyqtSignal(str)

    def __init__(self, user_id, action):
        super().__init__()
        self.setObjectName("SelectProductWindow")
        self.setWindowTitle(action)
        self.setGeometry(100, 100, 600, 400)
        self.user_id = user_id
        self.action = action

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Categoría", "Precio", "Stock"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        self.select_button = QPushButton(f"Seleccionar Producto para {action}")
        self.select_button.clicked.connect(self.select_product)
        layout.addWidget(self.select_button)

        self.setLayout(layout)

        self.load_stylesheet("style.css")
        self.load_products()

    def load_stylesheet(self, filename):
        style_file = QFile(filename)
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stylesheet = style_file.readAll()
            style_file.close()
            self.setStyleSheet(bytes(stylesheet).decode("utf-8"))

    def load_products(self):
        response = requests.get(f'http://127.0.0.1:5000/api/dashboard/{self.user_id}')
        if response.status_code == 200:
            products = response.json()
            self.table.setRowCount(len(products))

            for row, product in enumerate(products):
                item_id = QTableWidgetItem(product['_id'])
                item_name = QTableWidgetItem(product['name'])
                item_category = QTableWidgetItem(product['category'])
                item_price = QTableWidgetItem(f"${product.get('price', 'N/A')}")
                item_stock = QTableWidgetItem(product.get('stock', 'N/A'))

                self.table.setItem(row, 0, item_id)
                self.table.setItem(row, 1, item_name)
                self.table.setItem(row, 2, item_category)
                self.table.setItem(row, 3, item_price)
                self.table.setItem(row, 4, item_stock)
        

    def select_product(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            product_id = selected_items[0].text()
            self.product_selected.emit(product_id)
            self.close()

class ProductFormWindow(QWidget):
    product_saved = pyqtSignal()

    def __init__(self, user_id, action, product_id=None):
        super().__init__()
        self.setObjectName("ProductFormWindow")
        self.setWindowTitle(action)
        self.setGeometry(100, 100, 400, 300)
        self.user_id = user_id
        self.product_id = product_id

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.name_input = QLineEdit(self)
        form_layout.addRow("Nombre:", self.name_input)

        self.category_input = QLineEdit(self)
        form_layout.addRow("Categoría:", self.category_input)

        self.price_input = QDoubleSpinBox(self)
        self.price_input.setMaximum(1000000)
        form_layout.addRow("Precio:", self.price_input)

        self.stock_input = QLineEdit(self)
        form_layout.addRow("Stock:", self.stock_input)

        layout.addLayout(form_layout)

        self.save_button = QPushButton("Guardar", self)
        self.save_button.setObjectName("SaveButton")
        self.save_button.clicked.connect(self.save_product)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        self.load_stylesheet("style.css")

        if product_id:
            self.load_product()

    def load_stylesheet(self, filename):
        style_file = QFile(filename)
        if style_file.open(QFile.ReadOnly | QFile.Text):
            stylesheet = style_file.readAll()
            style_file.close()
            self.setStyleSheet(bytes(stylesheet).decode("utf-8"))

    def load_product(self):
        response = requests.get(f'http://127.0.0.1:5000/api/product/{self.product_id}')
        if response.status_code == 200:
            product = response.json()
            self.name_input.setText(product['name'])
            self.category_input.setText(product['category'])
            self.price_input.setValue(product.get('price', 0))
            self.stock_input.setText(product.get('stock', 'N/A'))
        

    def save_product(self):
        product_data = {
            "name": self.name_input.text(),
            "category": self.category_input.text(),
            "price": self.price_input.value(),
            "stock": self.stock_input.text()
        }

        if self.product_id:
            product_data["product_id"] = self.product_id
            response = requests.post('http://127.0.0.1:5000/api/update_product', json=product_data)
        else:
            product_data["user_id"] = self.user_id
            response = requests.post('http://127.0.0.1:5000/api/add_product', json=product_data)

        if response.status_code == 200:
            self.product_saved.emit()
            self.close()
        else:
            QMessageBox.warning(self, 'Error', 'Error al guardar el producto')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
