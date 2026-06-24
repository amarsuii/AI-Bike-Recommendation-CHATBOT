from flask import Flask, render_template, request, jsonify
import sqlite3
import re
import os

app = Flask(__name__)

DB_NAME = "bikes.db"


# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- CREATE DATABASE IF NOT EXISTS ----------
def init_db():
    if os.path.exists(DB_NAME):
        return

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE bikes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT NOT NULL,
            price INTEGER NOT NULL,
            mileage INTEGER NOT NULL,
            engine_cc INTEGER NOT NULL,
            horsepower INTEGER NOT NULL,
            category TEXT NOT NULL,
            image TEXT NOT NULL
        );
    """)

    sample_bikes = [
        ("Splendor Plus", "Hero", 85000, 60, 100, 8, "city", "splendor.jpg"),
        ("Shine", "Honda", 95000, 55, 125, 10, "city", "shine.jpg"),
        ("Pulsar 150", "Bajaj", 120000, 50, 150, 14, "city", "pulsar.jpg"),
        ("Unicorn 160", "Honda", 135000, 55, 162, 14, "city", "unicorn.jpg"),
        ("Apache RTR 160", "TVS", 130000, 50, 159, 15, "city", "apache160.jpg"),

        ("R15 V4", "Yamaha", 190000, 45, 155, 18, "sports", "r15.jpg"),
        ("MT-15", "Yamaha", 195000, 45, 155, 19, "sports", "mt15.jpg"),
        ("Ninja 300", "Kawasaki", 350000, 30, 296, 39, "sports", "ninja300.jpg"),

        ("Bullet Classic 350", "Royal Enfield", 220000, 35, 350, 20, "cruiser", "classic350.jpg"),
        ("Meteor 350", "Royal Enfield", 230000, 35, 350, 20, "cruiser", "meteor.jpg"),
        ("Harley X440", "Harley Davidson", 260000, 34, 440, 27, "cruiser", "harley440.jpg"),

        ("XPulse 200 4V", "Hero", 165000, 40, 199, 19, "adventure", "xpulse.jpg"),
        ("Himalayan 450", "Royal Enfield", 310000, 30, 452, 40, "adventure", "Himalayan.jpg"),
        ("BMW G310 GS", "BMW", 330000, 28, 313, 34, "adventure", "bmwgs.jpg"),

        ("Ather 450X", "Ather", 170000, 0, 0, 8, "electric", "ather450x.jpg"),
        ("TVS iQube", "TVS", 160000, 0, 0, 6, "electric", "iqube.jpg"),
        ("Ola S1 Pro", "Ola", 150000, 0, 0, 11, "electric", "olas1.jpg"),
        ("Revolt RV400", "Revolt", 160000, 0, 0, 9, "electric", "revolt.jpg"),
    ]

    cur.executemany("""
        INSERT INTO bikes (name, brand, price, mileage, engine_cc, horsepower, category, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_bikes)

    conn.commit()
    conn.close()
    print("Database initialized with sample bikes.")


init_db()


# ---------- HELPER FUNCTIONS ----------
def extract_budget(message: str):
    text = message.lower().replace(",", " ")

    if m := re.search(r'(\d+(\.\d+)?)\s*(lakh|lakhs|l)', text):
        return int(float(m.group(1)) * 100000)
    if m := re.search(r'(\d+(\.\d+)?)\s*k\b', text):
        return int(float(m.group(1)) * 1000)
    if m := re.search(r'\b(\d{5,7})\b', text):
        return int(m.group(1))
    return None


def detect_category(message: str):
    text = message.lower()

    if any(x in text for x in ["city", "daily", "office", "college", "commute", "mileage"]):
        return "city"
    if any(x in text for x in ["tour", "cruise", "highway", "travel", "trip", "long ride"]):
        return "cruiser"
    if any(x in text for x in ["sport", "race", "track", "speed", "fast"]):
        return "sports"
    if any(x in text for x in ["adventure", "offroad", "mountain", "xpulse", "himalayan"]):
        return "adventure"
    if any(x in text for x in ["electric", "battery", "charging", "ev"]):
        return "electric"
    return None


# ---------- RECOMMENDATION ----------
def recommend_bikes(message: str):
    budget = extract_budget(message)
    category = detect_category(message)

    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT * FROM bikes WHERE 1=1"
    params = []

    if budget:
        query += " AND price <= ?"
        params.append(budget)
    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY price ASC LIMIT 5"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "⚠️ No bikes found. Try changing your category or budget."

    response = ""
    for row in rows:
        price_lakh = row["price"] / 100000
        response += (
            f"<div class='bike-card'>"
            f"<img class='bike-photo' src='/static/images/{row['image']}'>"
            f"<div class='bike-info'>"
            f"<b>🏍 {row['brand']} {row['name']}</b><br>"
            f"💰 ₹{row['price']} (~{price_lakh:.2f} lakh)<br>"
            f"⛽ {row['mileage']} kmpl<br>"
            f"🚀 {row['engine_cc']}cc engine<br>"
            f"⚡ {row['horsepower']} HP<br>"
            f"🏷 {row['category']}"
            f"</div></div><br>"
        )

    return response


# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    if not user_message.strip():
        return jsonify({"reply": "Please type something 😊"})
    reply = recommend_bikes(user_message)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)
