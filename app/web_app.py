from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
import psycopg2
import psycopg2.extras

# --- Database config (change if needed) ---
DB_NAME = "FitnessClub"
DB_USER = "postgres"
DB_PASSWORD = "comp3005"
DB_HOST = "localhost"
DB_PORT = "5432"

# Simple trainer login (shared credentials)
TRAINER_USERNAME = "trainer"
TRAINER_PASSWORD = "fitness123"


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
)
app.secret_key = "supersecret"  # change for production


# ----------------- HOME / STATS -----------------


@app.route("/")
def index():
    """
    Home page with quick stats.
    Right now we pull live member count from the DB.
    """
    stats = {
        "members": None,
        "active_goals": None,   # placeholder for later
        "classes_today": None,  # placeholder for later
    }

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM members;")
                stats["members"] = cur.fetchone()[0]
    except Exception as e:
        print("Error loading home stats:", e)

    return render_template("index.html", stats=stats)


# ----------------- MEMBER FLOWS -----------------


@app.route("/members/portal", methods=["GET", "POST"])
def member_portal():
    """
    Simple member portal: user enters member ID OR email,
    and we redirect them to their dashboard.
    """
    if request.method == "POST":
        lookup = request.form.get("lookup", "").strip()

        if not lookup:
            flash("Enter a member ID or email.", "error")
            return redirect(url_for("member_portal"))

        try:
            with get_connection() as conn:
                with conn.cursor(
                    cursor_factory=psycopg2.extras.DictCursor
                ) as cur:
                    # If all digits, treat as ID, otherwise treat as email
                    if lookup.isdigit():
                        cur.execute(
                            "SELECT id FROM members WHERE id = %s;",
                            (int(lookup),),
                        )
                    else:
                        cur.execute(
                            "SELECT id FROM members WHERE email = %s;",
                            (lookup,),
                        )
                    row = cur.fetchone()
                    if not row:
                        flash("No member found with that ID or email.", "error")
                        return redirect(url_for("member_portal"))
                    member_id = row["id"]
        except Exception as e:
            print("Member portal lookup error:", e)
            flash("Database error while looking up member.", "error")
            return redirect(url_for("member_portal"))

        return redirect(url_for("member_dashboard", member_id=member_id))

    return render_template("member_portal.html")


@app.route("/members/register", methods=["GET", "POST"])
def member_register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip()
        dob = request.form.get("dob") or None
        gender = request.form.get("gender") or None
        phone = request.form.get("phone") or None

        if not full_name or not email:
            flash("Full name and email are required.", "error")
            return redirect(url_for("member_register"))

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO members (full_name, email, date_of_birth, gender, phone)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                        """,
                        (full_name, email, dob, gender, phone),
                    )
                    member_id = cur.fetchone()[0]
                    conn.commit()
            flash(f"Member registered successfully! ID: {member_id}", "success")
            return redirect(url_for("member_dashboard", member_id=member_id))
        except Exception as e:
            print("Error registering member:", e)
            flash("Database error while registering member.", "error")

    return render_template("member_register.html")


@app.route("/members/<int:member_id>/dashboard")
def member_dashboard(member_id):
    try:
        with get_connection() as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            ) as cur:
                # assumes you already created a view called member_dashboard
                cur.execute(
                    "SELECT * FROM member_dashboard WHERE member_id = %s;",
                    (member_id,),
                )
                row = cur.fetchone()
                if not row:
                    flash("Member not found in dashboard view.", "error")
                    return redirect(url_for("member_portal"))
                dashboard = dict(row)
    except Exception as e:
        print("Error loading dashboard:", e)
        flash("Database error while loading dashboard.", "error")
        return redirect(url_for("member_portal"))

    return render_template("member_dashboard.html", dashboard=dashboard)


@app.route("/members/<int:member_id>/metrics/add", methods=["POST"])
def add_health_metric(member_id):
    height = request.form.get("height")
    weight = request.form.get("weight")
    hr = request.form.get("heart_rate")
    body_fat = request.form.get("body_fat")

    def f_or_none(v):
        return float(v) if v else None

    def i_or_none(v):
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
                        member_id,
                        f_or_none(height),
                        f_or_none(weight),
                        i_or_none(hr),
                        f_or_none(body_fat),
                    ),
                )
                conn.commit()
        flash("Health metric added!", "success")
    except Exception as e:
        print("Error adding metric:", e)
        flash("Database error while adding metric.", "error")

    return redirect(url_for("member_dashboard", member_id=member_id))


# ----------------- TRAINER AUTH + DASHBOARD -----------------


@app.route("/trainer/login", methods=["GET", "POST"])
def trainer_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == TRAINER_USERNAME and password == TRAINER_PASSWORD:
            session["trainer_logged_in"] = True
            flash("Logged in as trainer.", "success")
            return redirect(url_for("trainer_portal"))

        flash("Invalid trainer credentials.", "error")
        return redirect(url_for("trainer_login"))

    return render_template("trainer_login.html")


@app.route("/trainer/logout")
def trainer_logout():
    session.pop("trainer_logged_in", None)
    flash("Trainer logged out.", "success")
    return redirect(url_for("index"))


@app.route("/trainer")
def trainer_portal():
    """
    Trainer dashboard.
    Shows trainers + upcoming PT sessions if those tables exist.
    Requires trainer login.
    """
    if not session.get("trainer_logged_in"):
        flash("Please log in as trainer to view that page.", "error")
        return redirect(url_for("trainer_login"))

    trainers = []
    sessions = []
    members = []

    try:
        with get_connection() as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            ) as cur:
                # Trainers
                cur.execute(
                    """
                    SELECT id, full_name, specialty
                    FROM trainers
                    ORDER BY full_name;
                    """
                )
                trainers = cur.fetchall()

                # Members for dropdown
                cur.execute(
                    """
                    SELECT id, full_name
                    FROM members
                    ORDER BY full_name;
                    """
                )
                members = cur.fetchall()

                # Upcoming sessions
                cur.execute(
                    """
                    SELECT
                        pts.id,
                        m.full_name AS member_name,
                        t.full_name AS trainer_name,
                        pts.session_date,
                        pts.session_time,
                        pts.status
                    FROM personal_training_sessions pts
                    JOIN members m ON pts.member_id = m.id
                    JOIN trainers t ON pts.trainer_id = t.id
                    ORDER BY pts.session_date, pts.session_time
                    LIMIT 10;
                    """
                )
                sessions = cur.fetchall()
    except Exception as e:
        print("Trainer portal query error:", e)

    return render_template(
        "trainer_portal.html",
        trainers=trainers,
        sessions=sessions,
        members=members,
    )


@app.route("/trainer/sessions/add", methods=["POST"])
def trainer_add_session():
    """
    Simple form for trainers to create a personal training session.
    """
    if not session.get("trainer_logged_in"):
        flash("Trainer login required.", "error")
        return redirect(url_for("trainer_login"))

    member_id = request.form.get("member_id")
    trainer_id = request.form.get("trainer_id")
    session_date = request.form.get("session_date")
    session_time = request.form.get("session_time")
    status = request.form.get("status") or "scheduled"

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO personal_training_sessions
                        (member_id, trainer_id, session_date, session_time, status)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (member_id, trainer_id, session_date, session_time, status),
                )
                conn.commit()
        flash("Training session created.", "success")
    except Exception as e:
        print("Error adding PT session:", e)
        flash("Database error while creating session.", "error")

    return redirect(url_for("trainer_portal"))


# ----------------- ADMIN DASHBOARD -----------------


@app.route("/admin")
def admin_portal():
    """
    Basic admin tools:
    - overview with total members
    - table of latest members
    """
    overview = {
        "total_members": None,
    }
    latest_members = []

    try:
        with get_connection() as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            ) as cur:
                cur.execute("SELECT COUNT(*) AS total_members FROM members;")
                overview["total_members"] = cur.fetchone()["total_members"]

                cur.execute(
                    """
                    SELECT id, full_name, email, date_of_birth
                    FROM members
                    ORDER BY id DESC
                    LIMIT 5;
                    """
                )
                latest_members = cur.fetchall()
    except Exception as e:
        print("Admin portal query error:", e)

    return render_template(
        "admin_portal.html",
        overview=overview,
        latest_members=latest_members,
    )


# ----------------- EQUIPMENT INVENTORY & RENTALS -----------------


@app.route("/equipment")
def equipment_portal():
    """
    Equipment inventory + rentals.
    Anyone can view; rentals are tied to members.
    """
    equipment = []
    active_rentals = []
    members = []

    try:
        with get_connection() as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.DictCursor
            ) as cur:
                # Equipment list
                cur.execute(
                    """
                    SELECT id, name, category, total_quantity, available_quantity
                    FROM equipment
                    ORDER BY name;
                    """
                )
                equipment = cur.fetchall()

                # Active rentals (not yet returned)
                cur.execute(
                    """
                    SELECT
                        er.id,
                        m.full_name AS member_name,
                        e.name AS equipment_name,
                        er.rented_on,
                        er.due_on
                    FROM equipment_rentals er
                    JOIN members m ON er.member_id = m.id
                    JOIN equipment e ON er.equipment_id = e.id
                    WHERE er.returned_on IS NULL
                    ORDER BY er.rented_on DESC;
                    """
                )
                active_rentals = cur.fetchall()

                # Members for dropdown
                cur.execute(
                    """
                    SELECT id, full_name
                    FROM members
                    ORDER BY full_name;
                    """
                )
                members = cur.fetchall()
    except Exception as e:
        print("Equipment portal query error:", e)

    return render_template(
        "equipment.html",
        equipment=equipment,
        active_rentals=active_rentals,
        members=members,
    )


@app.route("/equipment/add", methods=["POST"])
def add_equipment():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip() or None
    total_quantity = request.form.get("total_quantity")

    if not name or not total_quantity:
        flash("Name and quantity are required for equipment.", "error")
        return redirect(url_for("equipment_portal"))

    try:
        qty = int(total_quantity)
    except ValueError:
        flash("Quantity must be a number.", "error")
        return redirect(url_for("equipment_portal"))

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO equipment (name, category, total_quantity, available_quantity)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (name, category, qty, qty),
                )
                conn.commit()
        flash("Equipment item added.", "success")
    except Exception as e:
        print("Error adding equipment:", e)
        flash("Database error while adding equipment.", "error")

    return redirect(url_for("equipment_portal"))


@app.route("/equipment/rent", methods=["POST"])
def rent_equipment():
    member_id = request.form.get("member_id")
    equipment_id = request.form.get("equipment_id")
    rented_on = request.form.get("rented_on")
    due_on = request.form.get("due_on") or None

    if not member_id or not equipment_id or not rented_on:
        flash("Member, equipment, and rented-on date are required.", "error")
        return redirect(url_for("equipment_portal"))

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Check availability
                cur.execute(
                    "SELECT available_quantity FROM equipment WHERE id = %s FOR UPDATE;",
                    (equipment_id,),
                )
                row = cur.fetchone()
                if not row:
                    flash("Equipment not found.", "error")
                    return redirect(url_for("equipment_portal"))

                available = row[0]
                if available <= 0:
                    flash("No units available for that equipment.", "error")
                    return redirect(url_for("equipment_portal"))

                # Insert rental
                cur.execute(
                    """
                    INSERT INTO equipment_rentals
                        (member_id, equipment_id, rented_on, due_on)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (member_id, equipment_id, rented_on, due_on),
                )

                # Decrease available quantity
                cur.execute(
                    """
                    UPDATE equipment
                    SET available_quantity = available_quantity - 1
                    WHERE id = %s;
                    """,
                    (equipment_id,),
                )

                conn.commit()
        flash("Equipment rented out successfully.", "success")
    except Exception as e:
        print("Error renting equipment:", e)
        flash("Database error while renting equipment.", "error")

    return redirect(url_for("equipment_portal"))


@app.route("/equipment/return/<int:rental_id>", methods=["POST"])
def return_equipment(rental_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Find which equipment this rental is for
                cur.execute(
                    """
                    SELECT equipment_id
                    FROM equipment_rentals
                    WHERE id = %s AND returned_on IS NULL;
                    """,
                    (rental_id,),
                )
                row = cur.fetchone()
                if not row:
                    flash("Rental not found or already returned.", "error")
                    return redirect(url_for("equipment_portal"))

                equipment_id = row[0]

                # Mark as returned today
                cur.execute(
                    """
                    UPDATE equipment_rentals
                    SET returned_on = CURRENT_DATE
                    WHERE id = %s;
                    """,
                    (rental_id,),
                )

                # Increase available quantity
                cur.execute(
                    """
                    UPDATE equipment
                    SET available_quantity = available_quantity + 1
                    WHERE id = %s;
                    """,
                    (equipment_id,),
                )

                conn.commit()
        flash("Equipment returned.", "success")
    except Exception as e:
        print("Error returning equipment:", e)
        flash("Database error while returning equipment.", "error")

    return redirect(url_for("equipment_portal"))


# ----------------- MAIN -----------------


if __name__ == "__main__":
    app.run(debug=True)

