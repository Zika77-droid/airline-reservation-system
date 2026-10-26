import streamlit as st
import mysql.connector
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Airline Reservation System", page_icon="✈️", layout="wide")

# 2. Database Connection Helper
def get_connection():
    try:
        if "mysql" in st.secrets:
            db_config = st.secrets["mysql"]
            return mysql.connector.connect(
                host=db_config["host"],
                port=int(db_config["port"]),
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )
        else:
            return mysql.connector.connect(host="localhost", user="root", password="", database="airline_reservation_db")
    except Exception as e:
        return None

# Try Initializing Database Tables & Data
conn = get_connection()
if conn:
    try:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS flights (flight_id INT AUTO_INCREMENT PRIMARY KEY, flight_number VARCHAR(20), departure_airport VARCHAR(50), arrival_airport VARCHAR(50), departure_time VARCHAR(50), price DECIMAL(10,2), available_seats INT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS passengers (passenger_id INT AUTO_INCREMENT PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(50), email VARCHAR(100), passport_number VARCHAR(20))")
        cursor.execute("CREATE TABLE IF NOT EXISTS bookings (booking_id INT AUTO_INCREMENT PRIMARY KEY, flight_id INT, passenger_id INT, status VARCHAR(20) DEFAULT 'Confirmed')")
        cursor.execute("INSERT IGNORE INTO flights (flight_id, flight_number, departure_airport, arrival_airport, departure_time, price, available_seats) VALUES (1, 'MS-777', 'Cairo Intl (CAI)', 'Jeddah Intl (JED)', '2026-11-01 10:00:00', 350.00, 120), (2, 'MS-888', 'Cairo Intl (CAI)', 'Dubai Intl (DXB)', '2026-11-02 14:30:00', 420.00, 85)")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception:
        pass

# 3. Sidebar Navigation
st.sidebar.title("🎮 Control Panel")
page = st.sidebar.radio("Modules", [
    "🔍 Flight Search & Instant Booking",
    "👤 Passenger Management",
    "📊 Booking Records & Analytics",
    "➕ Schedule New Flight"
])

# 4. Main Header
st.title("✈️ Airline Reservation System")
st.caption("Centralized Real-Time Airline Reservation & Operations Platform")

# 5. Connection Test for UI
conn = get_connection()

if not conn:
    st.error("⚠️ لم يتم الاتصال بقاعدة البيانات أونلاين. يرجى التأكد من إعدادات Secrets.")
else:
    cursor = conn.cursor(dictionary=True)
    
    # Render Metrics Always
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        cursor.execute("SELECT COUNT(*) AS count FROM flights")
        f_count = cursor.fetchone()['count']
    except Exception:
        f_count = 0
        
    try:
        cursor.execute("SELECT SUM(available_seats) AS seats FROM flights")
        s_count = cursor.fetchone()['seats'] or 0
    except Exception:
        s_count = 0

    try:
        cursor.execute("SELECT COUNT(*) AS count FROM passengers")
        p_count = cursor.fetchone()['count']
    except Exception:
        p_count = 0

    try:
        cursor.execute("SELECT COUNT(*) AS count FROM bookings")
        b_count = cursor.fetchone()['count']
    except Exception:
        b_count = 0
    
    col1.metric("Total Scheduled Flights", f_count)
    col2.metric("Available Seat Inventory", s_count)
    col3.metric("Registered Passengers", p_count)
    col4.metric("Confirmed Bookings", b_count)
    
    st.divider()

    # PAGE 1: SEARCH & BOOKING
    if page == "🔍 Flight Search & Instant Booking":
        st.subheader("🔍 Search Active Flight Inventory")
        try:
            cursor.execute("SELECT flight_number, departure_airport, arrival_airport, departure_time, price, available_seats FROM flights")
            flights = cursor.fetchall()
            if flights:
                st.dataframe(pd.DataFrame(flights), use_container_width=True)
            else:
                st.info("No flights available.")
        except Exception as e:
            st.error(f"Error loading flights: {e}")

    # PAGE 2: PASSENGER MANAGEMENT
    elif page == "👤 Passenger Management":
        st.subheader("👤 Register New Passenger")
        with st.form("passenger_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email Address")
            passport = st.text_input("Passport Number")
            
            if st.form_submit_button("Register Passenger"):
                if first_name and last_name and email and passport:
                    try:
                        cursor.execute("INSERT INTO passengers (first_name, last_name, email, passport_number) VALUES (%s, %s, %s, %s)", (first_name, last_name, email, passport))
                        conn.commit()
                        st.success("Passenger registered successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error registering passenger: {e}")

    # PAGE 3: BOOKING RECORDS
    elif page == "📊 Booking Records & Analytics":
        st.subheader("📊 Active Booking Records")
        try:
            cursor.execute("SELECT * FROM bookings")
            b_data = cursor.fetchall()
            if b_data:
                st.dataframe(pd.DataFrame(b_data), use_container_width=True)
            else:
                st.info("No bookings recorded yet.")
        except Exception as e:
            st.error(f"Error loading bookings: {e}")

    # PAGE 4: SCHEDULE NEW FLIGHT
    elif page == "➕ Schedule New Flight":
        st.subheader("➕ Schedule New Flight Route")
        with st.form("flight_form"):
            flight_num = st.text_input("Flight Number (e.g. MS-101)")
            dep_airport = st.text_input("Departure Airport", "Cairo Intl (CAI)")
            arr_airport = st.text_input("Arrival Airport", "Dubai Intl (DXB)")
            dep_time = st.text_input("Departure Time", "2026-11-10 12:00:00")
            price = st.number_input("Ticket Price ($)", min_value=10.0, value=250.0)
            seats = st.number_input("Seat Capacity", min_value=1, value=150)
            
            if st.form_submit_button("Add Flight to Schedule"):
                if flight_num:
                    try:
                        cursor.execute("INSERT INTO flights (flight_number, departure_airport, arrival_airport, departure_time, price, available_seats) VALUES (%s, %s, %s, %s, %s, %s)", (flight_num, dep_airport, arr_airport, dep_time, price, seats))
                        conn.commit()
                        st.success("Flight added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding flight: {e}")

    cursor.close()
    conn.close()
