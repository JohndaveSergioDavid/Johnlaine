from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
import database
import uuid

app = Flask(__name__)
secret_key = str(uuid.uuid4())
app.secret_key = secret_key

db = database.db()

@app.route("/")
def root():
    return render_template('index.html')

@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM user WHERE username= ? AND password= ?", (username, password))
    user = cursor.fetchone()
    if user:
        role = user[3]
        if user[3] == "Administrator":
            return jsonify({"username": username, "role": role, "redirect_url": url_for('admin')})
        elif user[3] == "Adviser":
            return jsonify({"username": username, "role": role, "redirect_url": url_for('adviser')})
        elif user[3] == "Student":
            return jsonify({"username": username, "role": role, "redirect_url": url_for('student')})
        else:
            flash("Invalid role")
            return redirect(url_for('root'))
    else:
        flash("Wrong username or password")
        return redirect(url_for('root'))
    
@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/admin_settings")
def admin_settings():
    return render_template('admin_settings.html')

@app.route("/admin_users")
def admin_users():
    return render_template('admin_users.html')

@app.route("/admin_payments")
def admin_payments():
    return render_template('admin_payments.html')


@app.route("/api/count_total_students", methods=['GET'])
def api_count_total_students():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM user WHERE role='Student'")
        total_students = cursor.fetchone()[0]
        return jsonify({"total_students": total_students})
    except Exception as e:
        return str(e)
    
@app.route("/api/fetch_students_records", methods=['GET'])
def api_fetch_students_records():
    try:
        draw = request.args.get('draw')
        start = int(request.args.get('start'))
        length = int(request.args.get('length'))
        search_value = request.args.get('search[value]')
        order_column = request.args.get('order[0][column]')
        order_dir = request.args.get('order[0][dir]')
        
        columns = ['students.id', 'students.lrn', 'students.firstname', 'students.lastname', 'students.email', 'strand.name']
        order_by = columns[int(order_column)]
        
        cursor = db.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM students")
        total_records = cursor.fetchone()[0]
        
        # Fetch filtered records
        if search_value:
            query = f"""
                SELECT students.id, students.lrn, students.firstname, students.lastname, students.email, strand.name
                FROM students
                INNER JOIN strand ON students.strand_id = strand.id
                WHERE students.id LIKE ? OR students.lrn LIKE ? OR students.firstname LIKE ? OR students.lastname LIKE ? OR students.email LIKE ? OR strand.name LIKE ?
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', length, start))
        else:
            query = f"""
                SELECT students.id, students.lrn, students.firstname, students.lastname, students.email, strand.name
                FROM students
                INNER JOIN strand ON students.strand_id = strand.id
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (length, start))
        
        students = cursor.fetchall()
        
        # Count filtered records
        if search_value:
            cursor.execute("""
                SELECT COUNT(*)
                FROM students
                INNER JOIN strand ON students.strand_id = strand.id
                WHERE students.id LIKE ? OR students.lrn LIKE ? OR students.firstname LIKE ? OR students.lastname LIKE ? OR students.email LIKE ? OR strand.name LIKE ?
            """, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
            filtered_records = cursor.fetchone()[0]
        else:
            filtered_records = total_records
        
        data = []
        for student in students:
            data.append({
                'id': student[0],
                'lrn': student[1],
                'firstname': student[2],
                'lastname': student[3],
                'email': student[4],
                'strand': student[5]
            })
        
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        }
        
        return jsonify(response)
    except Exception as e:
        return str(e)
    
@app.route("/api/get_strand_choices", methods=['GET'])
def api_get_strand_choices():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM strand")
        strands = cursor.fetchall()
        return jsonify(strands)
    except Exception as e:
        return str(e)
    
    
@app.route("/api/add_student", methods=['POST'])
def api_add_student():
    try:
        lrn = request.form.get('lrn')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        strand_id = request.form.get('strand_id')
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        cursor = db.cursor()
        cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", (username, password, "Student"))
        login_id = cursor.lastrowid
        db.commit()
        cursor.execute("INSERT INTO students (lrn, firstname, lastname, email, strand_id, login_id) VALUES (?, ?, ?, ?, ?, ?)", (lrn, firstname, lastname, email, strand_id, login_id))
        db.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)