import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(
    page_title="Airline Reservation System",
    page_icon="✈️",
    layout="wide"
)

# 2. Database Connection Helper (Handles Cloud & Local Automatically)
def get_connection():
    try:
        if "mysql" in st.secrets:
            db_config = st.secrets["mysql"]
            conn = mysql.connector.connect(
                host=db_config["host"],
                port=int(db_config["port"]),
                user=db_config["user"],
                password=db_config["password"],
                database=db_config["database"]
            )
        else:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="airline_reservation_db"
            )
        
        cursor = conn.cursor()
        
        # 1. Flights Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flights (
                flight_id INT AUTO_INCREMENT PRIMARY KEY,
                flight_number VARCHAR(20) NOT NULL,
                departure_airport VARCHAR(50) NOT NULL,
                arrival_airport VARCHAR(50) NOT NULL,
                departure_time DATETIME NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                available_seats INT NOT NULL
            )
        """)
        
        # 2. Passengers Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passengers (
                passenger_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                passport_number VARCHAR(20) UNIQUE NOT NULL
            )
        """)
        
        # 3. Airports Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS airports (
                airport_id INT AUTO_INCREMENT PRIMARY KEY,
                airport_code VARCHAR(10) UNIQUE NOT NULL,
                airport_name VARCHAR(100) NOT NULL,
                city VARCHAR(50) NOT NULL,
                country VARCHAR(50) NOT NULL
            )
        """)
        
        # 4. Bookings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INT AUTO_INCREMENT PRIMARY KEY,
                flight_id INT,
                passenger_id INT,
                booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'Confirmed',
                FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE,
                FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id) ON DELETE CASCADE
            )
        """)
        
        # Insert Initial Sample Flights
        cursor.execute("""
            INSERT IGNORE INTO flights (flight_id, flight_number, departure_airport, arrival_airport, departure_time, price, available_seats) 
            VALUES 
            (1, 'MS-777', 'Cairo Intl (CAI)', 'Jeddah Intl (JED)', '2026-11-01 10:00:00', 350.00, 120),
            (2, 'MS-888', 'Cairo Intl (CAI)', 'Dubai Intl (DXB)', '2026-11-02 14:30:00', 420.00, 85),
            (3, 'MS-999', 'Cairo Intl (CAI)', 'London Heathrow (LHR)', '2026-11-05 08:15:00', 650.00, 45)
        """)
        
        conn.commit()
        cursor.close()
        return conn
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Helpers for Dropdowns
def get_airports():
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT airport_code, airport_name, city FROM airports")
        airports = cursor.fetchall()
        cursor.close()
        conn.close()
        return airports
    return []

def get_flights():
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT flight_id, flight_number, departure_airport, arrival_airport, price, available_seats FROM flights WHERE available_seats > 0")
        flights = cursor.fetchall()
        cursor.close()
        conn.close()
        return flights
    return []

def get_passengers():
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT passenger_id, first_name, last_name, passport_number FROM passengers")
        passengers = cursor.fetchall()
        cursor.close()
        conn.close()
        return passengers
    return []

# Navigation Sidebar
st.sidebar.title("🎮 Control Panel")
page = st.sidebar.radio("Modules", [
    "🔍 Flight Search & Instant Booking",
    "👤 Passenger Management",
    "📊 Booking Records & Analytics",
    "➕ Schedule New Flight"
])

# MAIN HEADER
st.title("✈️ Airline Reservation System")
st.caption("Centralized Real-Time Airline Reservation & Operations Platform")

conn = get_connection()

if conn and conn.is_connected():
    cursor = conn.cursor(dictionary=True)
    
    # Global Metrics Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    cursor.execute("SELECT COUNT(*) AS count FROM flights")
    total_flights = cursor.fetchone()['count']
    
    cursor.execute("SELECT SUM(available_seats) AS seats FROM flights")
    total_seats = cursor.fetchone()['seats'] or 0
    
    cursor.execute("SELECT COUNT(*) AS count FROM bookings WHERE status = 'Confirmed'")
    total_bookings = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) AS count FROM passengers")
    total_passengers = cursor.fetchone()['count']
    
    col1.metric("Total Scheduled Flights", total_flights)
    col2.metric("Available Seat Inventory", total_seats)
    col3.metric("Confirmed Bookings", total_bookings)
    col4.metric("Registered Passengers", total_passengers)
    
    st.divider()

    # PAGE 1: SEARCH & BOOKING
    if page == "🔍 Flight Search & Instant Booking":
        st.subheader("🔍 Search Active Flight Inventory")
        
        cursor.execute("SELECT flight_id, flight_number, departure_airport, arrival_airport, departure_time, price, available_seats FROM flights")
        flights_data = cursor.fetchall()
        
        if flights_data:
            df = pd.DataFrame(flights_data)
            df.columns = ["Flight ID", "Flight No", "Origin", "Destination", "Departure Time", "Price ($)", "Available Seats"]
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No flights available in inventory.")
            
        st.divider()
        st.subheader("🎟️ Book a Flight")
        
        passengers_list = get_passengers()
        flights_list = get_flights()
        
        if passengers_list and flights_list:
            with st.form("booking_form"):
                passenger_opt = st.selectbox("Select Passenger", options=passengers_list, format_func=lambda x: f"{x['first_name']} {x['last_name']} ({x['passport_number']})")
                flight_opt = st.selectbox("Select Flight", options=flights_list, format_func=lambda x: f"{x['flight_number']}: {x['departure_airport']} -> {x['arrival_airport']} (${x['price']})")
                
                submit_booking = st.form_submit_button("Confirm Reservation")
                
                if submit_booking:
                    try:
                        # Insert booking
                        cursor.execute("INSERT INTO bookings (flight_id, passenger_id) VALUES (%s, %s)", (flight_opt['flight_id'], passenger_opt['passenger_id']))
                        # Update seats
                        cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE flight_id = %s", (flight_opt['flight_id'],))
                        conn.commit()
                        st.success("Booking confirmed successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to complete booking: {e}")
        else:
            st.warning("Please ensure at least one passenger and one flight exist to place a booking.")

    # PAGE 2: PASSENGER MANAGEMENT
    elif page == "👤 Passenger Management":
        st.subheader("👤 Register New Passenger")
        with st.form("passenger_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email Address")
            passport = st.text_input("Passport Number")
            
            submit_passenger = st.form_submit_button("Register Passenger")
            if submit_passenger:
                if first_name and last_name and email and passport:
                    try:
                        cursor.execute("INSERT INTO passengers (first_name, last_name, email, passport_number) VALUES (%s, %s, %s, %s)", (first_name, last_name, email, passport))
                        conn.commit()
                        st.success("Passenger registered successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error registering passenger: {e}")
                else:
                    st.error("Please fill in all passenger fields.")
                    
        st.divider()
        st.subheader("📋 Registered Passengers List")
        cursor.execute("SELECT passenger_id, first_name, last_name, email, passport_number FROM passengers")
        p_data = cursor.fetchall()
        if p_data:
            st.dataframe(pd.DataFrame(p_data), use_container_width=True)

    # PAGE 3: BOOKING RECORDS
    elif page == "📊 Booking Records & Analytics":
        st.subheader("📊 Active Booking Master Ledger")
        query = """
            SELECT b.booking_id, f.flight_number, CONCAT(p.first_name, ' ', p.last_name) AS passenger_name, 
                   f.departure_airport, f.arrival_airport, b.booking_date, b.status
            FROM bookings b
            JOIN flights f ON b.flight_id = f.flight_id
            JOIN passengers p ON b.passenger_id = p.passenger_id
        """
        cursor.execute(query)
        b_data = cursor.fetchall()
        if b_data:
            st.dataframe(pd.DataFrame(b_data), use_container_width=True)
        else:
            st.info("No bookings recorded yet.")

    # PAGE 4: SCHEDULE NEW FLIGHT
    elif page == "➕ Schedule New Flight":
        st.subheader("➕ Schedule New Flight Route")
        with st.form("flight_form"):
            flight_num = st.text_input("Flight Number (e.g. MS-101)")
            dep_airport = st.text_input("Departure Airport", "Cairo Intl (CAI)")
            arr_airport = st.text_input("Arrival Airport", "Dubai Intl (DXB)")
            dep_time = st.date_input("Departure Date")
            price = st.number_input("Ticket Price ($)", min_value=10.0, value=250.0)
            seats = st.number_input("Seat Capacity", min_value=1, value=150)
            
            submit_flight = st.form_submit_button("Add Flight to Schedule")
            if submit_flight:
                if flight_num and dep_airport and arr_airport:
                    try:
                        cursor.execute(
                            "INSERT INTO flights (flight_number, departure_airport, arrival_airport, departure_time, price, available_seats) VALUES (%s, %s, %s, %s, %s, %s)",
                            (flight_num, dep_airport, arr_airport, str(dep_time), price, seats)
                        )
                        conn.commit()
                        st.success("Flight added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding flight: {e}")

    cursor.close()
    conn.close()
