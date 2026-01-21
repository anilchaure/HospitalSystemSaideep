import sqlite3
import os

DB_PATH = "hospital.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Only creates if file is missing. Delete hospital.db to refresh the doctor list.
    if not os.path.exists(DB_PATH):
        with get_db() as conn:
            # 1. Patients
            conn.execute('CREATE TABLE patients (id INTEGER PRIMARY KEY, name TEXT, disease TEXT, contact TEXT)')
            
            # 2. Doctors
            conn.execute('CREATE TABLE doctors (id INTEGER PRIMARY KEY, name TEXT, spec TEXT, fee REAL)')
            
            # 3. Appointments
            conn.execute('CREATE TABLE appointments (id INTEGER PRIMARY KEY, p_id INTEGER, d_id INTEGER, date TEXT)')
            
            # 4. Inventory
            conn.execute('CREATE TABLE inventory (id INTEGER PRIMARY KEY, item TEXT, stock INTEGER, price REAL)')
            
            # 5. Bills
            conn.execute('CREATE TABLE bills (id INTEGER PRIMARY KEY, p_name TEXT, amount REAL, date TEXT)')
            
            # --- Your Specific Specialist Team ---
            doctors_list = [
                ('Dr. Aryan', 'Cardiology', 800.0),
                ('Dr. Amir', 'General Physician', 500.0),
                ('Dr. Sunil', 'Dermatology', 700.0),
                ('Dr. Gaikwad', 'Otology (ENT)', 600.0),
                ('Dr. Pranjal', 'Neurology', 1500.0)
            ]
            
            conn.executemany("INSERT INTO doctors (name, spec, fee) VALUES (?, ?, ?)", doctors_list)
            
            # Initial Stock
            conn.execute("INSERT INTO inventory (item, stock, price) VALUES ('Paracetamol', 100, 10.0), ('Amoxicillin', 50, 120.0)")
            
            conn.commit()
        print("✅ Database Initialized with Aryan, Amir, Sunil, Gaikwad, and Pranjal.")
    else:
        print("📁 Database already exists. No changes made.")

if __name__ == "__main__":
    init_db()