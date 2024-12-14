import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, \
    QVBoxLayout, QLineEdit, QComboBox, QPushButton, QLabel, QToolBar, QStatusBar
from PyQt6.QtGui import QAction, QIcon
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

    @classmethod
    def update_student(cls, id, new_name, new_course, new_mobile):
        connection = sqlite3.connect(cls.database_path)
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (new_name, new_course, new_mobile, id))
        connection.commit()
        cursor.close()
        connection.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File")
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        help_menu_item = self.menuBar().addMenu("&Help")
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)

        edit_menu_item = self.menuBar().addMenu("&Edit")
        search_action = QAction(QIcon("icons/search.png"),"Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.table.cellClicked.connect(self.cell_clicked)
        self.setCentralWidget(self.table)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)
        self.addToolBar(toolbar)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

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
    
    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        buttons = self.findChildren(QPushButton)

        for button in buttons:
            self.statusbar.removeWidget(button)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)
    
    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
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

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        index = main_window.table.currentRow()
        self.student_id = main_window.table.item(index, 0).text()
        student_name = main_window.table.item(index, 1).text()
        course_name = main_window.table.item(index, 2).text()
        mobile = main_window.table.item(index, 3).text()

        layout = QVBoxLayout()
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        self.error_label = QLabel("")


        layout.addWidget(self.student_name)
        layout.addWidget(self.course_name)
        layout.addWidget(self.mobile)
        layout.addWidget(button)
        layout.addWidget(button)
        layout.addWidget(self.error_label)
        
        self.setLayout(layout)

    def update_student(self):
        new_name = self.student_name.text()
        new_course = self.course_name.itemText(self.course_name.currentIndex())
        new_mobile = self.mobile.text()

        DatabaseHandler.update_student(self.student_id, new_name, new_course, new_mobile)
        main_window.load_data()
        self.close()



class DeleteDialog(QDialog):
    pass

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())