import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

class DatabaseHandler():
    database_path = "database.db"

    @classmethod
    def get_all_students(cls):
        connection = sqlite3.connect(cls.database_path)

        result = connection.execute("SELECT * FROM students")
        result = list(result)

        connection.close()

        return result
    
    @classmethod
    def insert_student(cls, name, course, mobile):
        connection = sqlite3.connect(cls.database_path)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        file_menu_item = self.menuBar().addMenu("&File")
        add_student_action = QAction("Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        help_menu_item = self.menuBar().addMenu("&Help")
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        edit_menu_item = self.menuBar().addMenu("&Edit")
        search_action = QAction("Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        self.load_data()

    def load_data(self):
        result = DatabaseHandler.get_all_students()
            
        self.table.setRowCount(0)

        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)

            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        self.error_label = QLabel("")


        layout.addWidget(self.student_name)
        layout.addWidget(self.course_name)
        layout.addWidget(self.mobile)
        layout.addWidget(button)
        layout.addWidget(button)
        layout.addWidget(self.error_label)
        
        self.setLayout(layout)
    
    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()

        self.error_label.setText("")

        if not self.validate_student_dialog(name, course, mobile):
            self.error_label.setText("Invalid data!")
            return

        DatabaseHandler.insert_student(name, course, mobile)
        main_window.load_data()
        self.close()

    def validate_student_dialog(self, name, course, mobile):
        valid = True
        valid = valid and any(name) and any(course) and any(mobile)
        valid = valid and mobile.isnumeric()

        return valid

class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        button = QPushButton("Search")
        button.clicked.connect(self.search)

        layout.addWidget(self.student_name)
        layout.addWidget(button)
        
        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)

        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())