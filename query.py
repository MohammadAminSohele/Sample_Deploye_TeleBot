import psycopg2
from schema import db_url




def connect_to_db():
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    return conn, cursor

def insert_user(user_id, username):
    conn ,cursor = connect_to_db()

    cursor.execute("INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING", (user_id, username))

    conn.commit()
    conn.close()

def get_services():
    conn, cursor = connect_to_db()

    cursor.execute("SELECT service_id, name FROM services")
    services = cursor.fetchall()

    conn.close()
    return services

def get_dates(service_id):
    conn, cursor  = connect()

    cursor.execute("SELECT DISTINCT date FROM slots WHERE service_id = %s", (service_id,))
    dates = [row[0] for row in cursor.fetchall()]

    conn.close()
    return dates

def get_times(service_id, date):
    conn, cursor  = connect()

    cursor.execute("""
        SELECT slot_id, time FROM slots
        WHERE service_id = %s AND date = %s AND status = 'available'
        ORDER BY time ASC
    """, (service_id, date))
    times = cursor.fetchall()

    conn.close()
    return times

def book_appointments(user_id,slot_id):
    conn,cursor = connect()

    cursor.execute("INSERT INTO appointments (user_id,slot_id) VALUES(%s,%s)",(user_id,slot_id))

    conn.commit()
    conn.close()

def update_slots_status(slot_id):
    conn,cursor = connect()

    cursor.execute("UPDATE slots SET status = 'booked' WHERE slot_id=%s ",(slot_id,))

    conn.commit()
    conn.close()

def get_user_appointments(user_id):
    conn,cursor = connect()

    cursor.execute(
        """ 
        SELECT s.date,s.time,sv.name
        FROM appointments a
        JOIN slots s ON a.slot_id=s.slot_id
        JOIN services sv ON sv.service_id=s.service_id
        WHERE a.user_id=%s
        ORDER BY s.date,s.time
        """,(user_id,)
    )
    result = cursor.fetchall()
    conn.close()
    return result

def get_admin_appointments(admin_id):
    conn,cursor = connect_to_db()

    cursor.execute(
        """ 
        SELECT s.date,s.time,sv.name,u.username
        FROM appointments a
        JOIN slots s ON s.slot_id = a.slot_id
        JOIN services sv ON s.service_id = sv.service_id
        JOIN users u ON u.user_id = a.user_id
        WHERE sv.admin_id = %s
        ORDER BY s.date,s.time
        """,(admin_id,)
    )
    result = cursor.fetchall()
    conn.close()
    return result

def insert_slots(service_id,date,times):
    conn,cursor = connect_to_db()

    for time in times:
        cursor.execute("INSERT INTO slots (service_id,date,time,status) VALUES (%s,%s,%s,'available')",(service_id,date,time))

    conn.commit()
    conn.close()

def insert_service(name,admin_id):
    conn,cursor = connect()

    cursor.execute("INSERT INTO services (name,admin_id) VALUES (%s,%s)",(name,admin_id))
    service_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return service_id
