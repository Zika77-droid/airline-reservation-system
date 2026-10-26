import streamlit as st
import mysql.connector
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="Airline Reservation System", page_icon="✈️", layout="wide")

# Disable caching completely to update UI immediately
st.cache_data.clear()

# 2. Database Connection Helper
def get_connection():
    try:
        if "mysql" in st.secrets:
            db = st.secrets["mysql"]
            return mysql.connector.connect(
                host=db["host"], port=int(db["port"]), user=db["user"],
                password=db["password"], database=db["database"]
            )
        else:
            return mysql.connector.connect(host="localhost", user="root", password="", database="airline_reservation_db")
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

# Initializing Database Tables & Base Data
conn = get_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS flights (flight_id INT AUTO_INCREMENT PRIMARY KEY, flight_number VARCHAR(20), departure_airport VARCHAR(50), arrival_airport VARCHAR(50), departure_time VARCHAR(50), price DECIMAL(10,2), available_seats INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS passengers (passenger_id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(50), email VARCHAR(100), passport_number VARCHAR(20))")
    cursor.execute("CREATE TABLE IF NOT EXISTS bookings (booking_id INT AUTO_INCREMENT PRIMARY KEY, flight_id INT, passenger_id INT, status VARCHAR(20) DEFAULT 'Confirmed')")
    cursor.execute("INSERT IGNORE INTO flights (flight_id, flight_number, departure_airport, arrival_airport, departure_time, price, available_seats) VALUES (1, 'MS-777', 'Cairo (CAI)', 'Jeddah (JED)', '2026-11-01 10:00', 350.00, 120)")
    conn.commit()
    cursor.close()
    conn.close()

# 3. Main Header
st.title("✈️ Airline Reservation System")
st.divider()

# Radio buttons right on main screen or sidebar
action = st.radio("اختر العملية التي تريد القيام بها:", ["1. عرض الرحلات الحالية (View Flights)", "2. إضافة رحلة جديدة (Add Flight)", "3. تسجيل راكب جديد (Add Passenger)", "4. حجز تذكرة طيران (Book Ticket)"], horizontal=True)

st.divider()

conn = get_connection()
if conn:
    cursor = conn.cursor(dictionary=True)

    # OPTION 1: VIEW FLIGHTS
    if "1." in action:
        st.subheader("📋 قائمة الرحلات المسجلة في السيرفر")
        cursor.execute("SELECT flight_number, departure_airport, arrival_airport, departure_time, price, available_seats FROM flights")
        data = cursor.fetchall()
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.warning("لا توجد رحلات مسجلة.")

    # OPTION 2: ADD FLIGHT
    elif "2." in action:
        st.subheader("➕ نموذج إضافة رحلة جديدة")
        f_num = st.text_input("رقم الرحلة (مثال: MS-900)")
        dep = st.text_input("مطار المغادرة", "Cairo Intl (CAI)")
        arr = st.text_input("مطار الوصول", "Dubai Intl (DXB)")
        dep_time = st.text_input("تاريخ ووقت المغادرة", "2026-11-15 14:00")
        price = st.number_input("سعر التذكرة ($)", value=300.0)
        seats = st.number_input("عدد المقاعد المتاحة", value=100)
        
        if st.button("حفظ الرحلة في قاعدة البيانات"):
            if f_num and dep and arr:
                cursor.execute("INSERT INTO flights (flight_number, departure_airport, arrival_airport, departure_time, price, available_seats) VALUES (%s, %s, %s, %s, %s, %s)", (f_num, dep, arr, dep_time, price, seats))
                conn.commit()
                st.success(f"تم حفظ الرحلة {f_num} بنجاح في السيرفر!")
            else:
                st.error("يرجى ملء جميع البيانات المطلوب.")

    # OPTION 3: ADD PASSENGER
    elif "3." in action:
        st.subheader("👤 نموذج تسجيل راكب جديد")
        fname = st.text_input("الاسم الأول")
        lname = st.text_input("اسم العائلة")
        email = st.text_input("البريد الإلكتروني")
        passport = st.text_input("رقم پاسبور الراكب")
        
        if st.button("حفظ بيانات الراكب"):
            if fname and lname and passport:
                cursor.execute("INSERT INTO passengers (first_name, last_name, email, passport_number) VALUES (%s, %s, %s, %s)", (fname, lname, email, passport))
                conn.commit()
                st.success("تم تسجيل الراكب بنجاح!")
            else:
                st.error("يرجى ملء كافة البيانات.")

    # OPTION 4: BOOK TICKET
    elif "4." in action:
        st.subheader("🎟️ إتمام حجز تذكرة")
        cursor.execute("SELECT flight_id, flight_number FROM flights WHERE available_seats > 0")
        flights_list = cursor.fetchall()
        cursor.execute("SELECT passenger_id, first_name, last_name FROM passengers")
        passengers_list = cursor.fetchall()
        
        if flights_list and passengers_list:
            f_sel = st.selectbox("اختر الرحلة", options=flights_list, format_func=lambda x: x['flight_number'])
            p_sel = st.selectbox("اختر الراكب", options=passengers_list, format_func=lambda x: f"{x['first_name']} {x['last_name']}")
            
            if st.button("تاكيد الحجز"):
                cursor.execute("INSERT INTO bookings (flight_id, passenger_id) VALUES (%s, %s)", (f_sel['flight_id'], p_sel['passenger_id']))
                cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE flight_id = %s", (f_sel['flight_id'],))
                conn.commit()
                st.success("تم تأكيد الحجز بنجاح!")
        else:
            st.warning("يجب إضافة راكب ورحلة أولاً لكي تتمكن من الحجز.")

    cursor.close()
    conn.close()
