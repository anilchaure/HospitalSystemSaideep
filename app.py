from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from db_manager import get_db, init_db

app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = get_db()
    stats = {
        'p': conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
        'd': conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0],
        'r': conn.execute("SELECT SUM(amount) FROM bills").fetchone()[0] or 0
    }
    items = conn.execute("SELECT * FROM inventory LIMIT 5").fetchall()
    conn.close()
    return render_template('dashboard.html', stats=stats, items=items)

@app.route('/patients', methods=['GET', 'POST'])
def patients():
    conn = get_db()
    if request.method == 'POST':
        conn.execute("INSERT INTO patients (name, disease, contact) VALUES (?,?,?)",
                     (request.form['name'], request.form['disease'], request.form['contact']))
        conn.commit()
    data = conn.execute("SELECT * FROM patients").fetchall()
    conn.close()
    return render_template('patients.html', data=data)

@app.route('/appointments', methods=['GET', 'POST'])
def appointments():
    conn = get_db()
    if request.method == 'POST':
        conn.execute("INSERT INTO appointments (p_id, d_id, date) VALUES (?,?,?)",
                     (request.form['p_id'], request.form['d_id'], request.form['date']))
        conn.commit()
    data = conn.execute('''SELECT a.id, p.name as p_name, d.name as d_name, a.date 
                           FROM appointments a 
                           JOIN patients p ON a.p_id = p.id 
                           JOIN doctors d ON a.d_id = d.id''').fetchall()
    patients_list = conn.execute("SELECT * FROM patients").fetchall()
    doctors_list = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return render_template('appointments.html', data=data, patients=patients_list, doctors=doctors_list)

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    conn = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            conn.execute("INSERT INTO inventory (item, stock, price) VALUES (?, ?, ?)",
                         (request.form['item'], request.form['stock'], request.form['price']))
        elif action == 'delete':
            item_id = request.form.get('item_id')
            conn.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
    items = conn.execute("SELECT * FROM inventory").fetchall()
    conn.close()
    return render_template('inventory.html', items=items)

@app.route('/billing', methods=['GET', 'POST'])
def billing():
    conn = get_db()
    if request.method == 'POST':
        conn.execute("INSERT INTO bills (p_name, amount, date) VALUES (?,?,DATE('now'))",
                     (request.form['p_name'], request.form['amount']))
        conn.commit()
    
    # Get all past billing history
    data = conn.execute("SELECT * FROM bills ORDER BY id DESC").fetchall()
    
    # UPDATED LOGIC: Only fetch patients who HAVE an appointment BUT do NOT have a bill yet.
    # This ensures the same patient cannot be billed twice for the same visit.
    active_appts = conn.execute('''
        SELECT p.name as p_name, d.fee as doctor_fee 
        FROM appointments a
        JOIN patients p ON a.p_id = p.id
        JOIN doctors d ON a.d_id = d.id
        LEFT JOIN bills b ON p.name = b.p_name
        WHERE b.p_name IS NULL
    ''').fetchall()
    
    conn.close()
    return render_template('billing.html', data=data, appointments=active_appts)

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)