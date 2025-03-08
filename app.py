from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
import database
import uuid
import datetime

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
            id = user[0]
            cursor.execute("SELECT * FROM adviser WHERE login_id = ?", (id,))
            student = cursor.fetchone()
            return jsonify({"username": username, "role": role, "adviser_id": student[0], "redirect_url": url_for('adviser_summary')})
        elif user[3] == "Student":
            id = user[0]
            cursor.execute("SELECT * FROM students WHERE login_id = ?", (id,))
            student = cursor.fetchone()
            return jsonify({"username": username, "role": role, "student_id": student[0], "redirect_url": url_for('student_summary')})
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
    
@app.route("/api/get_payment_type", methods=['GET'])
def api_get_payment_type():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id, name, amount FROM payment_type")
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
    
@app.route("/api/update_student", methods=['POST'])
def api_update_student():
    try:
        id = request.form.get('id')
        lrn = request.form.get('lrn')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        strand_id = request.form.get('strand_id')
        
        cursor = db.cursor()
        cursor.execute("UPDATE students SET lrn=?, firstname=?, lastname=?, email=?, strand_id=? WHERE id=?", (lrn, firstname, lastname, email, strand_id, id))
        db.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return str(e)
    
@app.route("/api/add_payment", methods=['POST'])
def api_add_payment():
    try:
        student_id = request.form.get('student_id')
        payment_type_id = request.form.get('payment_type')
        amount = request.form.get('amount')
        status = request.form.get('status')
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = db.cursor()
        if status == "Fully Paid":
            completed_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO payments (student_id, transaction_timestamp, payment_type_id, amount, transaction_completed, status) VALUES (?, ?, ?, ?, ?, ?)", (student_id, timestamp, payment_type_id, amount, completed_date, status))
        else:
            cursor.execute("INSERT INTO payments (student_id, transaction_timestamp, payment_type_id, amount, status) VALUES (?, ?, ?, ?, ?)", (student_id, timestamp, payment_type_id, amount, status))
        db.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return str(e)
    
@app.route("/api/fetch_payments_records", methods=['GET'])
def api_fetch_payments_records():
    try:
        draw = request.args.get('draw')
        start = int(request.args.get('start'))
        length = int(request.args.get('length'))
        search_value = request.args.get('search[value]')
        order_column = request.args.get('order[0][column]')
        order_dir = request.args.get('order[0][dir]')
        
        columns = ['payments.id', 'payments.transaction_timestamp', 'payments.student_id', 'students.firstname || " " || students.lastname', 'payment_type.name', 'payments.amount', 'payments.status', 'payments.transaction_completed']
        order_by = columns[int(order_column)]
        
        cursor = db.cursor()
        
        # Count total records
        cursor.execute("SELECT COUNT(*) FROM payments")
        total_records = cursor.fetchone()[0]
        
        # Fetch filtered records
        if search_value:
            query = f"""
                SELECT payments.id, payments.transaction_timestamp, payments.student_id, students.firstname || ' ' || students.lastname AS name, payment_type.name AS payment_type, payments.amount, payments.status, payments.transaction_completed
                FROM payments
                INNER JOIN students ON payments.student_id = students.id
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                WHERE payments.id LIKE ? OR payments.student_id LIKE ? OR students.firstname LIKE ? OR students.lastname LIKE ? OR payment_type.name LIKE ? OR payments.amount LIKE ? OR payments.status LIKE ? OR payments.transaction_completed LIKE ?
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', length, start))
        else:
            query = f"""
                SELECT payments.id, payments.transaction_timestamp, payments.student_id, students.firstname || ' ' || students.lastname AS name, payment_type.name AS payment_type, payments.amount, payments.status, payments.transaction_completed
                FROM payments
                INNER JOIN students ON payments.student_id = students.id
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (length, start))
        
        payments = cursor.fetchall()
        
        # Count filtered records
        if search_value:
            cursor.execute("""
                SELECT COUNT(*)
                FROM payments
                INNER JOIN students ON payments.student_id = students.id
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                WHERE payments.id LIKE ? OR payments.student_id LIKE ? OR students.firstname LIKE ? OR students.lastname LIKE ? OR payment_type.name LIKE ? OR payments.amount LIKE ? OR payments.status LIKE ? OR payments.transaction_completed LIKE ?
            """, (f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
            filtered_records = cursor.fetchone()[0]
        else:
            filtered_records = total_records
        
        data = []
        for payment in payments:
            data.append({
                'id': payment[0],
                'transaction_timestamp': payment[1],
                'student_id': payment[2],
                'name': payment[3],
                'payment_type': payment[4],
                'amount': payment[5],
                'status': payment[6],
                'transaction_completed': payment[7]
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
    
@app.route("/api/get_energy_fee", methods=['GET'])
def api_get_energy_fee():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT SUM(amount) AS total FROM payments WHERE payment_type_id = 1 AND status = 'Fully Paid' GROUP BY payment_type_id;")
        energy_fee = cursor.fetchone()[0]
        return jsonify({"energy_fee": energy_fee})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/api/get_pending_fees", methods=['GET'])
def api_get_pending_fees():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT SUM(amount) AS total FROM payments WHERE status = 'Unpaid' GROUP BY status;")
        pending_fee = cursor.fetchone()[0]
        return jsonify({"pending_fee": pending_fee})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/api/get_fully_paid_fees", methods=['GET'])
def get_fully_paid_fees():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT SUM(amount) AS total FROM payments WHERE status = 'Fully Paid' GROUP BY status;")
        full_fee = cursor.fetchone()[0]
        return jsonify({"full_fee": full_fee})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/get_strand_id", methods=['GET'])
def api_get_strand_id():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM strand WHERE name = ?", (request.args.get('strand_name'),))
        strand_id = cursor.fetchone()[0]
        return jsonify(strand_id)
    except Exception as e:
        return str(e)
    

@app.route("/api/get_payment_type_id", methods=['GET'])
def get_payment_type_id():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM payment_type WHERE name = ?", (request.args.get('payment_type_name'),))
        payment_type_id = cursor.fetchone()
        return jsonify(payment_type_id)
    except Exception as e:
        return str(e)
    
@app.route("/api/get_payment_type_amount", methods=['GET'])
def get_payment_type_amount():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT amount FROM payment_type WHERE id = ?", (request.args.get('payment_type_id'),))
        amount = cursor.fetchone()
        return jsonify(amount)
    except Exception as e:
        return str(e)
    
    
@app.route("/api/update_payment", methods=['POST'])
def api_update_payment():
    try:
        id = request.form.get('id')
        status = request.form.get('status')
        payment_type_id = request.form.get('payment_type')
        amount = request.form.get('amount')
        print(status)
        print(payment_type_id)
        print(amount)
        cursor = db.cursor()
        if status == "Fully Paid":
            completed_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE payments SET status=?, payment_type_id = ?, amount = ?, transaction_completed=? WHERE id=?", (status, payment_type_id, amount, completed_date, id))
        else:
            cursor.execute("UPDATE payments SET status=?, payment_type_id = ?, amount = ?, transaction_completed=? WHERE id=?", (status, payment_type_id, amount, None, id))
        db.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return str(e)
    
@app.route("/student_summary")
def student_summary():
    return render_template('student_summary.html')

@app.route("/adviser_summary")
def adviser_summary():
    return render_template('adviser_summary.html')

@app.route("/get_student_info", methods=['GET'])
def get_student_info():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM students WHERE login_id = ?", (request.args.get('login_id'),))
        student = cursor.fetchone()
        return jsonify(student)
    except Exception as e:
        return str(e)
    
    
@app.route("/api/fetch_payments_student", methods=['GET'])
def api_fetch_payments_student():
    try:
        draw = request.args.get('draw')
        start = int(request.args.get('start'))
        length = int(request.args.get('length'))
        search_value = request.args.get('search[value]')
        order_column = request.args.get('order[0][column]')
        order_dir = request.args.get('order[0][dir]')
        student_id = request.args.get('student_id')
        
        columns = ['payments.id', 'payments.transaction_timestamp', 'payment_type.name', 'payments.amount', 'payments.status', 'payments.transaction_completed']
        order_by = columns[int(order_column)]
        
        cursor = db.cursor()
        
        # Count total records for the specific student
        cursor.execute("SELECT COUNT(*) FROM payments WHERE student_id = ?", (student_id,))
        total_records = cursor.fetchone()[0]
        
        # Fetch filtered records
        if search_value:
            query = f"""
                SELECT payments.id, payments.transaction_timestamp, payment_type.name AS payment_type, payments.amount, payments.status, payments.transaction_completed
                FROM payments
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                WHERE student_id = ? AND (payments.id LIKE ? OR payment_type.name LIKE ? OR payments.amount LIKE ? OR payments.status LIKE ? OR payments.transaction_completed LIKE ?)
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (student_id, f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', length, start))
        else:
            query = f"""
                SELECT payments.id, payments.transaction_timestamp, payment_type.name AS payment_type, payments.amount, payments.status, payments.transaction_completed
                FROM payments
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                WHERE payments.student_id = ?
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (student_id, length, start))
        
        payments = cursor.fetchall()
        
        # Count filtered records
        if search_value:
            cursor.execute("""
                SELECT COUNT(*)
                FROM payments
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                WHERE payments.student_id = ? AND (payments.id LIKE ? OR payment_type.name LIKE ? OR payments.amount LIKE ? OR payments.status LIKE ? OR payments.transaction_completed LIKE ?)
            """, (student_id, f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
            filtered_records = cursor.fetchone()[0]
        else:
            filtered_records = total_records
        
        data = []
        for payment in payments:
            data.append({
                'id': payment[0],
                'transaction_timestamp': payment[1],
                'payment_type': payment[2],
                'amount': payment[3],
                'status': payment[4],
                'transaction_completed': payment[5]
            })
        
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        }
        print(response)
        
        return jsonify(response)
    except Exception as e:
        return str(e)
    
@app.route("/api/fetch_section_handle", methods=['GET'])
def api_fetch_section_handle():
    try:
        draw = request.args.get('draw')
        start = int(request.args.get('start'))
        length = int(request.args.get('length'))
        search_value = request.args.get('search[value]')
        order_column = request.args.get('order[0][column]')
        order_dir = request.args.get('order[0][dir]')
        adviser_id = request.args.get('adviser_id')
        
        columns = ['section.id', 'section.name']
        order_by = columns[int(order_column)]
        
        cursor = db.cursor()
        
        # Count total records for the specific adviser
        cursor.execute("SELECT COUNT(*) FROM section WHERE adviser_id = ?", (adviser_id,))
        total_records = cursor.fetchone()[0]
        
        # Fetch filtered records
        if search_value:
            query = f"""
                SELECT section.id, section.name
                FROM section
                WHERE adviser_id = ? AND (section.id LIKE ? OR section.name LIKE ?)
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (adviser_id, f'%{search_value}%', f'%{search_value}%', length, start))
        else:
            query = f"""
                SELECT section.id, section.name
                FROM section
                WHERE adviser_id = ?
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (adviser_id, length, start))
        
        sections = cursor.fetchall()
        
        # Count filtered records
        if search_value:
            cursor.execute("""
                SELECT COUNT(*)
                FROM section
                WHERE adviser_id = ? AND (section.id LIKE ? OR section.name LIKE ?)
            """, (adviser_id, f'%{search_value}%', f'%{search_value}%'))
            filtered_records = cursor.fetchone()[0]
        else:
            filtered_records = total_records
        
        data = []
        for section in sections:
            data.append({
                'id': section[0],
                'name': section[1]
            })
        
        response = {
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@app.route("/api/adviser_fetch_payments_records", methods=['GET'])
def adviser_fetch_payments_records():
    try:
        draw = request.args.get('draw')
        start = int(request.args.get('start'))
        length = int(request.args.get('length'))
        search_value = request.args.get('search[value]')
        order_column = request.args.get('order[0][column]')
        order_dir = request.args.get('order[0][dir]')
        adviser_id = request.args.get('adviser_id')  # Assuming adviser_id is passed as a query parameter
        
        columns = ['payments.id', 'payments.transaction_timestamp', 'section.name', 'payments.student_id', 'students.firstname || " " || students.lastname', 'payment_type.name', 'payments.amount', 'payments.status', 'payments.transaction_completed']
        order_by = columns[int(order_column)]
        
        cursor = db.cursor()
        
        # Count total records
        cursor.execute("""
            SELECT COUNT(*)
            FROM payments
            INNER JOIN students ON payments.student_id = students.id
            INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
            INNER JOIN section_info ON section_info.student_id = students.id
            INNER JOIN section ON section.id = section_info.section_id
            INNER JOIN adviser ON adviser.id = section.adviser_id
            WHERE section.adviser_id = ?
        """, (adviser_id,))
        total_records = cursor.fetchone()[0]
        
        # Fetch filtered records
        if search_value:
            query = f"""
                SELECT payments.id, payments.transaction_timestamp, section.name, payments.student_id, students.firstname || ' ' || students.lastname AS name, payment_type.name AS payment_type, payments.amount, payments.status, payments.transaction_completed
                FROM payments
                INNER JOIN students ON payments.student_id = students.id
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                INNER JOIN section_info ON section_info.student_id = students.id
                INNER JOIN section ON section.id = section_info.section_id
                INNER JOIN adviser ON adviser.id = section.adviser_id
                WHERE section.adviser_id = ? AND (payments.id LIKE ? OR payments.student_id LIKE ? OR students.firstname LIKE ? OR students.lastname LIKE ? OR payment_type.name LIKE ? OR payments.amount LIKE ? OR payments.status LIKE ? OR payments.transaction_completed LIKE ?)
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (adviser_id, f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', length, start))
        else:
            query = f"""
                SELECT payments.id, payments.transaction_timestamp, section.name, payments.student_id, students.firstname || ' ' || students.lastname AS name, payment_type.name AS payment_type, payments.amount, payments.status, payments.transaction_completed
                FROM payments
                INNER JOIN students ON payments.student_id = students.id
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                INNER JOIN section_info ON section_info.student_id = students.id
                INNER JOIN section ON section.id = section_info.section_id
                INNER JOIN adviser ON adviser.id = section.adviser_id
                WHERE section.adviser_id = ?
                ORDER BY {order_by} {order_dir}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (adviser_id, length, start))
        
        payments = cursor.fetchall()
        
        # Count filtered records
        if search_value:
            cursor.execute("""
                SELECT COUNT(*)
                FROM payments
                INNER JOIN students ON payments.student_id = students.id
                INNER JOIN payment_type ON payments.payment_type_id = payment_type.id
                INNER JOIN section_info ON section_info.student_id = students.id
                INNER JOIN section ON section.id = section_info.section_id
                INNER JOIN adviser ON adviser.id = section.adviser_id
                WHERE section.adviser_id = ? AND (payments.id LIKE ? OR payments.student_id LIKE ? OR students.firstname LIKE ? OR students.lastname LIKE ? OR payment_type.name LIKE ? OR payments.amount LIKE ? OR payments.status LIKE ? OR payments.transaction_completed LIKE ?)
            """, (adviser_id, f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%', f'%{search_value}%'))
            filtered_records = cursor.fetchone()[0]
        else:
            filtered_records = total_records
        
        data = []
        for payment in payments:
            data.append({
                'id': payment[0],
                'transaction_timestamp': payment[1],
                'section_name': payment[2],
                'student_id': payment[3],
                'name': payment[4],
                'payment_type': payment[5],
                'amount': payment[6],
                'status': payment[7],
                'transaction_completed': payment[8]
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
    
@app.route("/generate_chart", methods=['GET'])
def generate_chart():
    try:
        cursor = db.cursor()
        
        # SQL query to get the sum of payments per day for the last 7 days
        sql = """
            SELECT DATE(transaction_completed) AS transaction_date, SUM(amount) AS total_amount
            FROM payments
            WHERE status = 'Fully Paid'
              AND transaction_completed >= DATE('now', '-7 days')
            GROUP BY DATE(transaction_completed)
            ORDER BY transaction_date;
        """
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # Format data for Chart.js
        labels = []
        data = []
        for row in results:
            labels.append(row['transaction_date'])  # Dates for the X-axis
            data.append(row['total_amount'])       # Amounts for the Y-axis
        
        # Return data as JSON
        return jsonify({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)