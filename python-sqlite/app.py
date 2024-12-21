from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import sqlite3
import bleach
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Student {self.name}>'
    
# Fungsi untuk validasi nama
def validate_name(name):
    return bool(re.match("^[A-Za-z ]+$", name))

# Fungsi untuk validasi angka positif
def validate_age(age):
    return age > 0

# Fungsi untuk validasi grade
def validate_grade(grade):
    valid_grades = ['A', 'AB', 'B', 'BC', 'C', 'D', 'E']
    return grade in valid_grades


@app.route('/')
def index():
    # RAW Query
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', students=students)

@app.route('/add', methods=['POST', 'GET'])
def add_student():
    errors = []  # List untuk menyimpan pesan error

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']

        # Konversi usia ke integer
        try:
            age = int(age)
        except ValueError:
            errors.append("Usia harus berupa angka positif.")
        # Validasi input
        if not validate_name(name):
            errors.append("Nama hanya boleh mengandung huruf A-Z atau a-z.")
        if not validate_age(age):
            errors.append("Usia harus lebih besar dari 0.")
        if not validate_grade(grade):
            errors.append("Grade tidak valid. Pilih dari A, AB, B, BC, C, D, E.")
        # Jika tidak ada error, simpan data
        if not errors:
            safe_name = bleach.clean(name)  # Sanitasi input
            connection = sqlite3.connect('instance/students.db')
            cursor = connection.cursor()

            # Tetap gunakan RAW query seperti sebelumnya
            query = f"INSERT INTO student (name, age, grade) VALUES ('{safe_name}', {age}, '{grade}')"
            cursor.execute(query)
            connection.commit()
            connection.close()
            return redirect(url_for('index'))

    # Jika ada error, tampilkan kembali halaman form dengan error
    students = db.session.execute(text('SELECT * FROM student')).fetchall()
    return render_template('index.html', errors=errors, students=students)



@app.route('/delete/<string:id>') 
def delete_student(id):
    # RAW Query
    db.session.execute(text(f"DELETE FROM student WHERE id={id}"))
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        
        # RAW Query
        db.session.execute(text(f"UPDATE student SET name='{name}', age={age}, grade='{grade}' WHERE id={id}"))
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # RAW Query
        student = db.session.execute(text(f"SELECT * FROM student WHERE id={id}")).fetchone()
        return render_template('edit.html', student=student)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)

