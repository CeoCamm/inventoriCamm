from PyQt5.QtWidgets import *
import requests

class EditProductWindow(QDialog):
    def __init__(self, product_id):
        super().__init__()

        self.product_id = product_id

        self.setWindowTitle('Editar Producto')

        self.name_label = QLabel('Nombre:')
        self.name_edit = QLineEdit()

        self.category_label = QLabel('Categoría:')
        self.category_edit = QLineEdit()

        self.stock_label = QLabel('Stock: ')
        self.stick_edit = QLineEdit()

        self.price_label = QLabel('Precio: ')
        self.price_edit = QDoubleSpinBox()
        self.price_edit.setPrefix("$ ")
        self.price_edit.setMinimum(0.0)

        self.save_button = QPushButton('Guardar Cambios')
        self.save_button.clicked.connect(self.save_changes)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.category_label)
        layout.addWidget(self.category_edit)
        layout.addWidget(self.stock_label)
        layout.addWidget(self.stock_edit)
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_edit)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_changes(self):
        name = self.name_edit.text()
        category = self.category_edit.text()
        stock = self.stock_edit.text()
        price = self.price_edit.value()

        data = {
            'product_id': self.product_id,
            'name': name,
            'category': category,
            'stock': stock,
            'price': price
        }

        response = requests.post('http://localhost:5000/api/edit_product', json=data)

        if response.status_code == 200:
            QMessageBox.information(self, 'Éxito', 'Producto editado exitosamente.')
            self.accept()  # Cerrar la ventana después de guardar cambios
        else:
            QMessageBox.warning(self, 'Error', 'Hubo un problema al editar el producto.')

        self.close()