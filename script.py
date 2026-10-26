import streamlit as st
import mysql.connector
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Airline Reservation System",
    page_icon="✈️",
    layout="wide"
)

# 2. Database Connection Helper
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
        
        # Tables Creation
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passengers (
                passenger_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                passport_number VARCHAR(20) UNIQUE NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS airports (
                airport_id INT AUTO_INCREMENT PRIMARY KEY,
                airport_code VARCHAR(10) UNIQUE NOT NULL,
                airport_name VARCHAR(100) NOT NULL,
                city VARCHAR(50) NOT NULL,
                country VARCHAR(50) NOT NULL
            )
        """)
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
        
        # Insert Initial Sample Data
        cursor.execute("""
            INSERT IGNORE INTO flights (flight_id, flight_number, departure_airport, arrival_airport, departure_time, price, available_seats) 
            VALUES 
            (1, 'MS-777', 'Cairo Intl (CAI)', 'Jeddah Intl (JED)', '2026-11-01 10:00:00', 350.00, 120),
            (2, 'MS-888', 'Cairo Intl (CAI)', 'Dubai Intl (DXB)', '2026-11-02 14:30:00', 420.00, 85)
        """)
        
        conn.commit()
        cursor.close()
        return conn
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# 3. Sidebar Selection
st.sidebar.title("🎮 Operations Menu")
option = st.sidebar.selectbox(
    "Select Action:",
    ["📊 View Dashboard & Flights", "➕ Add New Flight", "👤 Add New Passenger", "🎟️ Book a Ticket"]
)

st.title("✈️ Airline Reservation System")

conn = get_connection()

if conn and conn.is_connected():
    cursor = conn.cursor(dictionary=True)

    # ACTION 1: DASHBOARD
    if option == "📊 View Dashboard & Flights":
        st.subheader("✈️ Active Scheduled Flights")
        cursor.execute("SELECT flight_number, departure_airport, arrival_airport, departure_time, price, available_seats FROM flights")
        flights = cursor.fetchall()
        if flights:
            st.dataframe(pd.DataFrame(flights), use_container_width=True)
        else:
            st.info("No flights available.")

    # ACTION 2: ADD FLIGHT FORM
    elif option == "➕ Add New Flight":
        st.subheader("➕ Schedule a New Flight Route")
        with st.form("add_flight_form"):
            f_num = st.text_input("Flight Number (e.g., MS-101)")
            dep = st.text_input("Departure Airport", "Cairo Intl (CAI)")
            arr = st.text_input("Arrival Airport", "Dubai Intl (DXB)")
            dep_time = st.text_input("Departure Time (YYYY-MM-DD HH:MM:SS)", "2026-11-10 12:00:00")
            price = st.number_input("Price ($)", min_value=10.0, value=200.0)
            seats = st.number_input("Available Seats", min_value=1, value=100)
            
            submit = st.form_submit_button("Submit & Save Flight")
            if submit:
                if f_num and dep and arr:
                    try:
                        cursor.execute(
                            "INSERT INTO flights (flight_number, departure_airport, arrival_airport, departure_time, price, available_seats) VALUES (%s, %s, %s, %s, %s, %s)",
                            (f_num, dep, arr, dep_time, price, seats)
                        )
                        conn.commit()
                        st.success(f"Flight {f_num} added successfully to Database!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ACTION 3: ADD PASSENGER FORM
    elif option == "👤 Add New Passenger":
        st.subheader("👤 Register Passenger Details")
        with st.form("add_passenger_form"):
            fname = st.text_input("First Name")
            lname = st.text_input("Last Name")
            email = st.text_input("Email")
            passport = st.text_input("Passport Number")
            
            submit = st.form_submit_button("Register Passenger")
            if submit:
                if fname and lname and email and passport:
                    try:
                        cursor.execute(
                            "INSERT INTO passengers (first_name, last_name, email, passport_number) VALUES (%s, %s, %s, %s)",
                            (fname, lname, email, passport)
                        )
                        conn.commit()
                        st.success("Passenger registered successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ACTION 4: BOOK TICKET
    elif option == "🎟️ Book a Ticket":
        st.subheader("🎟️ Reserve a Seat")
        cursor.execute("SELECT flight_id, flight_number FROM flights WHERE available_seats > 0")
        flights_list = cursor.fetchall()
        cursor.execute("SELECT passenger_id, first_name, last_name FROM passengers")
        passengers_list = cursor.fetchall()
        
        if flights_list and passengers_list:
            with st.form("booking_form"):
                flight_sel = st.selectbox("Select Flight", options=flights_list, format_func=lambda x: x['flight_number'])
                passenger_sel = st.selectbox("Select Passenger", options=passengers_list, format_func=lambda x: f"{x['first_name']} {x['last_name']}")
                
                submit = st.form_submit_button("Confirm Booking")
                if submit:
                    try:
                        cursor.execute("INSERT INTO bookings (flight_id, passenger_id) VALUES (%s, %s)", (flight_sel['flight_id'], passenger_sel['passenger_id']))
                        cursor.execute("UPDATE flights SET available_seats = available_seats - 1 WHERE flight_id = %s", (flight_sel['flight_id'],))
                        conn.commit()
                        st.success("Ticket Booked Successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("Please add at least one passenger and one flight first.")

    cursor.close()
    conn.close()
