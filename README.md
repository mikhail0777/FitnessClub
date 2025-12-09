👤 Author

Mikhail Simanian — Full-Stack Developer / Student Entrepreneur
📍 Ottawa, Canada — Carleton University
📧 miksim077@gmail.com

🏋️‍♂️ FitnessClub — A Database-Backed Gym Management Web Platform

FitnessClub is a streamlined fitness center management system that helps gyms efficiently track:

✔ Members
✔ Personal training sessions
✔ Equipment inventory & rentals
✔ Administrative insights

Built using:

🐍 Python (Flask web framework)

🐘 PostgreSQL (relational database)

🎨 HTML + CSS for clean UI design

This project turns a classic PostgreSQL database assignment into a full web application with real-world workflows and a modern UX.
🚀 Live Demo (Future Deployment Plan)

✨ Feature Overview
Role	Capabilities
Members	Track profile data, register, log workouts (future)
Trainers	View members, assign PT sessions, track schedule
Admin	View dashboards, manage database statistics
Staff	Rent out equipment, update availability

Additional highlights:

📊 Dashboard analytics pulling real database counts

🏷 Organized equipment categories + rental tracking

🔐 Separate trainer login page

🧱 Clean and scalable SQL schema

🔮 Roadmap / Future Enhancements
Status	Upcoming Feature
⏳ Planned	Class scheduling & enrollment
⏳ Planned	Embedded charts on dashboards
⏳ Planned	Member progress tracking (goals, metrics)
⏳ Planned	Admin authentication and roles system
⏳ Planned	Cloud hosting + demo login
🧠 Purpose

This project demonstrates:

✔ Full-stack software design
✔ Data modeling + SQL logic
✔ CRUD operations with real UI
✔ Clean workflow for gyms & institutions

Turned an academic database into a real usable product.
Showcases strong backend development, database integration, and UI design skills.

----------------------------------------
🛠️ Local Setup & Running the App

You need:

✔ Python 3.11+
✔ PostgreSQL 14+ installed
✔ A local database named: FitnessClub

1️⃣ Clone the repo
git clone https://github.com/mikhail0777/FitnessClub.git
cd FitnessClub

2️⃣ Install backend dependencies
pip install -r requirements.txt

3️⃣ Import the database schema + demo data

Inside PostgreSQL / pgAdmin:

1️⃣ Run sql/DDL.sql → creates tables
2️⃣ Run sql/seed_demo_data.sql → fills demo members, trainers, equipment

4️⃣ Start the Flask server
python app/web_app.py


📌 The app runs at:
👉 http://127.0.0.1:5000/

📂 Project Structure
FitnessClub/
│ app/
│ ├─ main.py
│ ├─ web_app.py        # Main Flask app
│ sql/
│ ├─ DDL.sql           # Database schema
│ ├─ seed_demo_data.sql # Demo test data
│ templates/            # HTML Templates (Jinja2)
│ static/
│ ├─ styles.css         # UI Stylesheet
│ requirements.txt
│ README.md

