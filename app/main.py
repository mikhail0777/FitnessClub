# app/main.py
# Simple CLI application for Fitness Club Management System
# Uses PostgreSQL via psycopg2
# Student: Mikhail Simanian (101303853)

import psycopg2
import psycopg2.extras
from datetime import datetime

DB_NAME = "FitnessClub"
DB_USER = "postgres"
DB_PASSWORD = "comp3005"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def register_member():
    print("\n=== Member Registration ===")
    full_name = input("Full name: ").strip()
    email = input("Email: ").strip()
    dob_str = input("Date of birth (YYYY-MM-DD, or blank): ").strip()
    gender = input("Gender (optional): ").strip()
    phone = input("Phone (optional): ").strip()

    dob = None
    if dob_str:
        try:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format, skipping DOB.")

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO members (full_name, email, date_of_birth, gender, phone)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (full_name, email, dob, gender if gender else None, phone if phone else None)
                )
                member_id = cur.fetchone()[0]
        print(f"Member registered successfully with ID {member_id}.")
    except psycopg2.Error as e:
        print("Error registering member:", e)


def add_health_metric():
    print("\n=== Add Health Metric ===")
    member_id = input("Member ID: ").strip()
    height = input("Height (cm, optional): ").strip()
    weight = input("Weight (kg, optional): ").strip()
    hr = input("Heart rate (bpm, optional): ").strip()
    body_fat = input("Body fat (% , optional): ").strip()

    def to_num_or_none(v):
        return float(v) if v else None

    def to_int_or_none(v):
        return int(v) if v else None

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO health_metrics
                    (member_id, height_cm, weight_kg, heart_rate_bpm, body_fat_percent)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        int(member_id),
                        to_num_or_none(height),
                        to_num_or_none(weight),
                        to_int_or_none(hr),
                        to_num_or_none(body_fat),
                    )
                )
        print("Health metric added successfully.")
    except psycopg2.Error as e:
        print("Error adding health metric:", e)


def show_member_dashboard():
    print("\n=== Member Dashboard ===")
    member_id = input("Member ID: ").strip()

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    "SELECT * FROM member_dashboard WHERE member_id = %s;",
                    (int(member_id),)
                )
                row = cur.fetchone()
                if not row:
                    print("Member not found in dashboard view.")
                    return

                print(f"\nDashboard for {row['full_name']} ({row['email']})")
                print(f"Latest weight (kg): {row['latest_weight_kg']}")
                print(f"Latest heart rate (bpm): {row['latest_heart_rate_bpm']}")
                print(f"Active goals: {row['active_goal_count']}")
                print(f"Past classes attended: {row['past_class_count']}")
                print(f"Upcoming PT sessions: {row['upcoming_session_count']}")
    except psycopg2.Error as e:
        print("Error fetching dashboard:", e)


def schedule_pt_session():
    print("\n=== Schedule PT Session ===")
    member_id = int(input("Member ID: ").strip())
    trainer_id = int(input("Trainer ID: ").strip())
    room_id = int(input("Room ID: ").strip())
    start_str = input("Start time (YYYY-MM-DD HH:MM): ").strip()
    end_str = input("End time (YYYY-MM-DD HH:MM): ").strip()
    price = float(input("Price: ").strip())

    try:
        start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid datetime format.")
        return

    if end_time <= start_time:
        print("End time must be after start time.")
        return

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM personal_training_sessions
                    WHERE trainer_id = %s
                      AND status = 'scheduled'
                      AND NOT (end_time <= %s OR start_time >= %s);
                    """,
                    (trainer_id, start_time, end_time)
                )
                (conflicts_trainer,) = cur.fetchone()
                if conflicts_trainer > 0:
                    print("Trainer is not available in that time slot.")
                    return

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM personal_training_sessions
                    WHERE room_id = %s
                      AND status = 'scheduled'
                      AND NOT (end_time <= %s OR start_time >= %s);
                    """,
                    (room_id, start_time, end_time)
                )
                (conflicts_room_pt,) = cur.fetchone()
                if conflicts_room_pt > 0:
                    print("Room is already booked for another PT session in that time slot.")
                    return

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM group_classes
                    WHERE room_id = %s
                      AND NOT (end_time <= %s OR start_time >= %s);
                    """,
                    (room_id, start_time, end_time)
                )
                (conflicts_room_class,) = cur.fetchone()
                if conflicts_room_class > 0:
                    print("Room is in use for a group class in that time slot.")
                    return

                cur.execute(
                    """
                    INSERT INTO personal_training_sessions
                    (member_id, trainer_id, room_id, start_time, end_time, status, price)
                    VALUES (%s, %s, %s, %s, %s, 'scheduled', %s)
                    RETURNING id;
                    """,
                    (member_id, trainer_id, room_id, start_time, end_time, price)
                )
                session_id = cur.fetchone()[0]
        print(f"PT session scheduled successfully with ID {session_id}.")
    except psycopg2.Error as e:
        print("Error scheduling PT session:", e)


def register_for_class():
    print("\n=== Register for Group Class ===")
    member_id = int(input("Member ID: ").strip())
    class_id = int(input("Class ID: ").strip())

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO class_registrations (member_id, class_id)
                    VALUES (%s, %s);
                    """,
                    (member_id, class_id)
                )
        print("Registration successful.")
    except psycopg2.Error as e:
        print("Error registering for class:", e)
        print("This might be due to class capacity, duplicate registration, or invalid IDs.")


def trainer_view_schedule():
    print("\n=== Trainer Schedule View ===")
    trainer_id = int(input("Trainer ID: ").strip())

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                print("\n-- Upcoming Personal Training Sessions --")
                cur.execute(
                    """
                    SELECT pts.id, m.full_name AS member_name,
                           pts.start_time, pts.end_time, pts.status, pts.price
                    FROM personal_training_sessions pts
                    JOIN members m ON pts.member_id = m.id
                    WHERE pts.trainer_id = %s
                      AND pts.start_time >= NOW()
                    ORDER BY pts.start_time;
                    """,
                    (trainer_id,)
                )
                rows = cur.fetchall()
                if not rows:
                    print("No upcoming PT sessions.")
                else:
                    for r in rows:
                        print(f"Session {r['id']}: {r['member_name']} "
                              f"{r['start_time']} - {r['end_time']} "
                              f"(status={r['status']}, price={r['price']})")

                print("\n-- Upcoming Group Classes --")
                cur.execute(
                    """
                    SELECT gc.id, gc.title, gc.start_time, gc.end_time, r.name AS room_name
                    FROM group_classes gc
                    JOIN rooms r ON gc.room_id = r.id
                    WHERE gc.trainer_id = %s
                      AND gc.start_time >= NOW()
                    ORDER BY gc.start_time;
                    """,
                    (trainer_id,)
                )
                rows = cur.fetchall()
                if not rows:
                    print("No upcoming group classes.")
                else:
                    for r in rows:
                        print(f"Class {r['id']}: {r['title']} in {r['room_name']} "
                              f"{r['start_time']} - {r['end_time']}")
    except psycopg2.Error as e:
        print("Error fetching trainer schedule:", e)


def trainer_member_lookup():
    print("\n=== Trainer Member Lookup ===")
    name_part = input("Enter part of member name (case-insensitive): ").strip()

    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, full_name, email
                    FROM members
                    WHERE LOWER(full_name) LIKE LOWER(%s)
                    ORDER BY full_name;
                    """,
                    (f"%{name_part}%",)
                )
                members = cur.fetchall()
                if not members:
                    print("No members match that search.")
                    return

                print("\nMatching members:")
                for m in members:
                    print(f"{m['id']}: {m['full_name']} ({m['email']})")

                member_id = int(input("\nEnter member ID to inspect: ").strip())

                print("\n-- Active Goals --")
                cur.execute(
                    """
                    SELECT goal_type, target_value, unit, description
                    FROM fitness_goals
                    WHERE member_id = %s AND is_active = TRUE;
                    """,
                    (member_id,)
                )
                goals = cur.fetchall()
                if not goals:
                    print("No active goals.")
                else:
                    for g in goals:
                        print(f"{g['goal_type']} => target {g['target_value']} {g['unit']} "
                              f"({g['description']})")

                print("\n-- Latest Metric --")
                cur.execute(
                    """
                    SELECT recorded_at, height_cm, weight_kg, heart_rate_bpm, body_fat_percent
                    FROM health_metrics
                    WHERE member_id = %s
                    ORDER BY recorded_at DESC
                    LIMIT 1;
                    """,
                    (member_id,)
                )
                metric = cur.fetchone()
                if not metric:
                    print("No metrics found for this member.")
                else:
                    print(f"Recorded at: {metric['recorded_at']}")
                    print(f"Height (cm): {metric['height_cm']}")
                    print(f"Weight (kg): {metric['weight_kg']}")
                    print(f"Heart rate (bpm): {metric['heart_rate_bpm']}")
                    print(f"Body fat (%): {metric['body_fat_percent']}")
    except psycopg2.Error as e:
        print("Error during member lookup:", e)


def admin_create_class():
    print("\n=== Admin: Create Group Class ===")
    title = input("Class title: ").strip()
    trainer_id = int(input("Trainer ID: ").strip())
    room_id = int(input("Room ID: ").strip())
    start_str = input("Start time (YYYY-MM-DD HH:MM): ").strip()
    end_str = input("End time (YYYY-MM-DD HH:MM): ").strip()
    capacity = int(input("Capacity: ").strip())
    base_price = float(input("Base price: ").strip())

    try:
        start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Invalid datetime format.")
        return

    if end_time <= start_time:
        print("End time must be after start time.")
        return

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM group_classes
                    WHERE room_id = %s
                      AND NOT (end_time <= %s OR start_time >= %s);
                    """,
                    (room_id, start_time, end_time)
                )
                (conflicts_gc,) = cur.fetchone()
                if conflicts_gc > 0:
                    print("Room is already booked for another class in that time slot.")
                    return

                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM personal_training_sessions
                    WHERE room_id = %s
                      AND status = 'scheduled'
                      AND NOT (end_time <= %s OR start_time >= %s);
                    """,
                    (room_id, start_time, end_time)
                )
                (conflicts_pt,) = cur.fetchone()
                if conflicts_pt > 0:
                    print("Room is booked for a PT session in that time slot.")
                    return

                cur.execute(
                    """
                    INSERT INTO group_classes
                    (title, trainer_id, room_id, start_time, end_time, capacity, base_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (title, trainer_id, room_id, start_time, end_time, capacity, base_price)
                )
                class_id = cur.fetchone()[0]
        print(f"Group class created with ID {class_id}.")
    except psycopg2.Error as e:
        print("Error creating group class:", e)


def admin_generate_invoice():
    print("\n=== Admin: Generate Invoice ===")
    member_id = int(input("Member ID: ").strip())
    num_items = int(input("How many line items? ").strip())

    items = []
    for i in range(num_items):
        print(f"\nItem {i+1}:")
        item_type = input("Item type (membership/pt_session/class): ").strip()
        description = input("Description: ").strip()
        quantity = int(input("Quantity: ").strip())
        unit_price = float(input("Unit price: ").strip())
        line_total = quantity * unit_price
        items.append((item_type, description, quantity, unit_price, line_total))

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO invoices (member_id, total_amount, status)
                    VALUES (%s, 0, 'unpaid')
                    RETURNING id;
                    """,
                    (member_id,)
                )
                invoice_id = cur.fetchone()[0]

                for item in items:
                    cur.execute(
                        """
                        INSERT INTO invoice_line_items
                        (invoice_id, item_type, description, quantity, unit_price, line_total)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        (invoice_id,) + item
                    )

                cur.execute(
                    """
                    UPDATE invoices
                    SET total_amount = (
                        SELECT COALESCE(SUM(line_total), 0)
                        FROM invoice_line_items
                        WHERE invoice_id = %s
                    )
                    WHERE id = %s;
                    """,
                    (invoice_id, invoice_id)
                )
        print(f"Invoice {invoice_id} created successfully.")
    except psycopg2.Error as e:
        print("Error generating invoice:", e)


def member_menu():
    while True:
        print("\n=== Member Menu ===")
        print("1) Register new member")
        print("2) Add health metric")
        print("3) Show dashboard")
        print("4) Schedule PT session")
        print("5) Register for group class")
        print("0) Back to main menu")
        choice = input("Choose: ").strip()

        if choice == "1":
            register_member()
        elif choice == "2":
            add_health_metric()
        elif choice == "3":
            show_member_dashboard()
        elif choice == "4":
            schedule_pt_session()
        elif choice == "5":
            register_for_class()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def trainer_menu():
    while True:
        print("\n=== Trainer Menu ===")
        print("1) View schedule")
        print("2) Member lookup")
        print("0) Back to main menu")
        choice = input("Choose: ").strip()

        if choice == "1":
            trainer_view_schedule()
        elif choice == "2":
            trainer_member_lookup()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def admin_menu():
    while True:
        print("\n=== Admin Menu ===")
        print("1) Create group class")
        print("2) Generate invoice")
        print("0) Back to main menu")
        choice = input("Choose: ").strip()

        if choice == "1":
            admin_create_class()
        elif choice == "2":
            admin_generate_invoice()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")


def main():
    print("Health & Fitness Club Management System (CLI)")
    while True:
        print("\n=== Main Menu ===")
        print("1) Member functions")
        print("2) Trainer functions")
        print("3) Admin functions")
        print("0) Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            member_menu()
        elif choice == "2":
            trainer_menu()
        elif choice == "3":
            admin_menu()
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
