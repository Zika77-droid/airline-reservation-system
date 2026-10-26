import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import pandas as pd

# 1. Page Configuration
st.set_page_config(
    page_title="Airline Reservation System",
    page_icon="✈️",
    layout="wide"
)


# 2. Database Connection Helper
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
        return conn
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None
        


# Helper to fetch active airports for dropdowns
def get_airports():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT airport_code, city FROM airports")
        airports = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        conn.close()
        return ["ALL"] + airports
    return ["ALL"]


# 3. Main Header & Banner
st.title("✈️ Airline Reservation System")
st.caption("Centralized Real-Time Airline Reservation & Operations Platform")
st.markdown("---")

# 4. Top KPI Dashboard Overview
conn = get_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM flights")
    total_flights = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(available_seats) FROM flights")
    total_seats = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'")
    active_bookings = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM passengers")
    total_passengers = cursor.fetchone()[0]
    conn.close()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Scheduled Flights", total_flights)
    m2.metric("Available Seat Inventory", total_seats)
    m3.metric("Confirmed Bookings", active_bookings)
    m4.metric("Registered Passengers", total_passengers)
    st.markdown("---")

# 5. Sidebar Navigation
st.sidebar.title("🎮 Control Panel")
choice = st.sidebar.radio("Modules", [
    "🔍 Flight Search & Instant Booking",
    "👤 Passenger Management",
    "📋 Booking Records & Analytics",
    "➕ Schedule New Flight"
])

# MODULE 1: SEARCH & BOOK
if choice == "🔍 Flight Search & Instant Booking":
    st.subheader("🔍 Search Active Flight Inventory")

    airport_options = get_airports()

    col1, col2 = st.columns(2)
    with col1:
        orig_selection = st.selectbox("Origin Airport (From)", airport_options)
    with col2:
        dest_selection = st.selectbox("Destination Airport (To)", airport_options)

    orig_code = orig_selection.split(" - ")[0] if orig_selection != "ALL" else ""
    dest_code = dest_selection.split(" - ")[0] if dest_selection != "ALL" else ""

    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT flight_id, flight_number, departure_airport, arrival_airport, departure_time, price, available_seats FROM flights WHERE available_seats > 0"
        params = []

        if orig_code:
            query += " AND departure_airport = %s"
            params.append(orig_code)
        if dest_code:
            query += " AND arrival_airport = %s"
            params.append(dest_code)

        cursor.execute(query, tuple(params))
        flights = cursor.fetchall()
        conn.close()

        if flights:
            df_flights = pd.DataFrame(flights)
            df_flights.columns = ["Flight ID", "Flight No", "Origin", "Destination", "Departure Time", "Price ($)",
                                  "Available Seats"]
            st.dataframe(df_flights, use_container_width=True)

            st.markdown("### 🎟️ Reserve Ticket")
            b_col1, b_col2, b_col3 = st.columns([2, 2, 1])
            with b_col1:
                selected_flight_id = st.number_input("Enter Flight ID", min_value=1, step=1)
            with b_col2:
                passenger_id = st.number_input("Enter Passenger ID", min_value=1, step=1)
            with b_col3:
                st.write("")
                st.write("")
                book_btn = st.button("Confirm Booking", type="primary", use_container_width=True)

            if book_btn:
                conn = get_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT available_seats FROM flights WHERE flight_id = %s",
                                       (selected_flight_id,))
                        res = cursor.fetchone()
                        if res and res[0] > 0:
                            today = datetime.now().strftime('%Y-%m-%d')
                            cursor.execute(
                                "INSERT INTO bookings (passenger_id, flight_id, booking_date, status) VALUES (%s, %s, %s, 'Confirmed')",
                                (passenger_id, selected_flight_id, today))
                            cursor.execute(
                                "UPDATE flights SET available_seats = available_seats - 1 WHERE flight_id = %s",
                                (selected_flight_id,))
                            conn.commit()
                            st.success(f"🎉 Booking Confirmed! Ticket issued for Passenger #{passenger_id}.")
                            st.rerun()
                        else:
                            st.error("Invalid Flight ID or no available seats remaining!")
                    except Error as e:
                        conn.rollback()
                        st.error(f"Transaction Error: {e}")
                    finally:
                        conn.close()
        else:
            st.info("No matching flights available.")

# MODULE 2: PASSENGER REGISTRATION
elif choice == "👤 Passenger Management":
    st.subheader("👤 Passenger Directory & Registration")

    tab_reg, tab_view = st.tabs(["Register Passenger", "View All Passengers"])

    with tab_reg:
        with st.form("passenger_form"):
            full_name = st.text_input("Full Name (as in passport)")
            passport = st.text_input("Passport Number")
            phone = st.text_input("Contact Phone Number")
            submit = st.form_submit_button("Register Passenger")

            if submit:
                if full_name and passport and phone:
                    conn = get_connection()
                    if conn:
                        try:
                            cursor = conn.cursor()
                            query = "INSERT INTO passengers (full_name, passport_number, phone) VALUES (%s, %s, %s)"
                            cursor.execute(query, (full_name, passport, phone))
                            conn.commit()
                            st.success(
                                f"Passenger registered successfully! Assigned Passenger ID: **{cursor.lastrowid}**")
                        except Error as e:
                            st.error(f"Failed to register: {e}")
                        finally:
                            conn.close()
                else:
                    st.warning("Please complete all required fields.")

    with tab_view:
        conn = get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT passenger_id AS 'Passenger ID', full_name AS 'Full Name', passport_number AS 'Passport Number', phone AS 'Phone' FROM passengers")
            passengers = cursor.fetchall()
            conn.close()
            if passengers:
                st.dataframe(pd.DataFrame(passengers), use_container_width=True)

# MODULE 3: MANAGE BOOKINGS
elif choice == "📋 Booking Records & Analytics":
    st.subheader("📋 Central Reservation Ledger")

    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT b.booking_id AS 'Booking ID', p.full_name AS 'Passenger Name', p.passport_number AS 'Passport', f.flight_number AS 'Flight No', f.price AS 'Fare ($)', b.booking_date AS 'Booking Date', b.status AS 'Status'
                FROM bookings b
                         JOIN passengers p ON b.passenger_id = p.passenger_id
                         JOIN flights f ON b.flight_id = f.flight_id
                ORDER BY b.booking_id DESC \
                """
        cursor.execute(query)
        bookings = cursor.fetchall()
        conn.close()

        if bookings:
            st.dataframe(pd.DataFrame(bookings), use_container_width=True)

            st.markdown("### ❌ Cancellation Desk")
            c_col1, c_col2 = st.columns([3, 1])
            with c_col1:
                cancel_id = st.number_input("Enter Booking ID to Process Cancellation", min_value=1, step=1)
            with c_col2:
                st.write("")
                st.write("")
                cancel_btn = st.button("Cancel Booking", type="primary")

            if cancel_btn:
                conn = get_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT flight_id, status FROM bookings WHERE booking_id = %s", (cancel_id,))
                        record = cursor.fetchone()
                        if record:
                            flight_id, status = record[0], record[1]
                            if status != 'Cancelled':
                                cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s",
                                               (cancel_id,))
                                cursor.execute(
                                    "UPDATE flights SET available_seats = available_seats + 1 WHERE flight_id = %s",
                                    (flight_id,))
                                conn.commit()
                                st.success("Booking cancelled and seat seat inventory updated!")
                                st.rerun()
                            else:
                                st.warning("Selected booking is already marked as Cancelled.")
                        else:
                            st.error("Booking ID not found.")
                    except Error as e:
                        conn.rollback()
                        st.error(f"Error: {e}")
                    finally:
                        conn.close()
        else:
            st.info("No booking transactions found.")

# MODULE 4: ADD FLIGHT SCHEDULE
elif choice == "➕ Schedule New Flight":
    st.subheader("➕ Create Flight Schedule")

    airports_list = [a for a in get_airports() if a != "ALL"]

    with st.form("add_flight_form"):
        f_num = st.text_input("Flight Code (e.g. MS900)")

        c1, c2 = st.columns(2)
        with c1:
            dep_choice = st.selectbox("Departure Airport", airports_list)
        with c2:
            arr_choice = st.selectbox("Arrival Airport", airports_list)

        f_time = st.text_input("Departure Time", value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        c3, c4 = st.columns(2)
        with c3:
            f_price = st.number_input("Ticket Price ($)", min_value=10.0, value=350.0, step=10.0)
        with c4:
            f_seats = st.number_input("Aircraft Seat Capacity", min_value=1, value=150, step=5)

        submit_flight = st.form_submit_button("Publish Flight Schedule")
        if submit_flight:
            dep_code = dep_choice.split(" - ")[0]
            arr_code = arr_choice.split(" - ")[0]

            if dep_code == arr_code:
                st.error("Departure and Arrival airports cannot be identical!")
            elif f_num and f_time:
                conn = get_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        query = """INSERT INTO flights (flight_number, departure_airport, arrival_airport, \
                                                        departure_time, price, available_seats)
                                   VALUES (%s, %s, %s, %s, %s, %s)"""
                        cursor.execute(query, (f_num.upper(), dep_code, arr_code, f_time, f_price, f_seats))
                        conn.commit()
                        st.success(f"Flight {f_num.upper()} successfully published!")
                        st.rerun()
                    except Error as e:
                        st.error(f"Failed to add flight: {e}")
                    finally:
                        conn.close()
            else:
                st.warning("Please provide a valid flight number and departure time.")
