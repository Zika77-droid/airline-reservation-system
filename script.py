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
                    cancel_conn = get_connection()
                    if cancel_conn is not None:
                        try:
                            cancel_cursor = cancel_conn.cursor()
                            cancel_cursor.execute(
                                "SELECT flight_id, status FROM bookings WHERE booking_id = %s FOR UPDATE",
                                (int(cancel_id),),
                            )
                            record = cancel_cursor.fetchone()
                            if not record:
                                st.error("Booking ID not found.")
                            elif record[1] == "Cancelled":
                                st.warning("Selected booking is already marked as Cancelled.")
                            else:
                                flight_id = record[0]
                                cancel_cursor.execute(
                                    "UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s",
                                    (int(cancel_id),),
                                )
                                cancel_cursor.execute(
                                    "UPDATE flights SET available_seats = available_seats + 1 WHERE flight_id = %s",
                                    (flight_id,),
                                )
                                cancel_conn.commit()
                                st.success("Booking cancelled and seat inventory updated!")
                                st.rerun()
                        except Error as exc:
                            cancel_conn.rollback()
                            st.error(f"Cancellation failed: {exc}")
                        finally:
                            cancel_conn.close()
            else:
                st.info("No booking transactions found.")
        except Error as exc:
            st.error(f"Could not load booking records: {exc}")
        finally:
            conn.close()

# MODULE 4: ADD FLIGHT SCHEDULE
elif choice == "➕ Schedule New Flight":
    st.subheader("➕ Create Flight Schedule")
    airport_options = [airport for airport in get_airports() if airport != "ALL"]

    if not airport_options:
        st.warning("No airports are available. Check the database connection and airports table.")
    else:
        with st.form("add_flight_form"):
            f_num = st.text_input("Flight Code (e.g. MS900)")
            c1, c2 = st.columns(2)
            with c1:
                dep_choice = st.selectbox("Departure Airport", airport_options)
            with c2:
                arr_choice = st.selectbox("Arrival Airport", airport_options)
            f_time = st.text_input(
                "Departure Time", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
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
                elif not f_num.strip() or not f_time.strip():
                    st.warning("Please provide a valid flight number and departure time.")
                else:
                    conn = get_connection()
                    if conn is not None:
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                """
                                INSERT INTO flights
                                    (flight_number, departure_airport, arrival_airport,
                                     departure_time, price, available_seats)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """,
                                (f_num.strip().upper(), dep_code, arr_code, f_time.strip(), f_price, int(f_seats)),
                            )
                            conn.commit()
                            st.success(f"Flight {f_num.strip().upper()} successfully published!")
                            st.rerun()
                        except Error as exc:
                            conn.rollback()
                            st.error(f"Failed to add flight: {exc}")
                        finally:
                            conn.close()
