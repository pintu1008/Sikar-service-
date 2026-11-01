import os, sqlite3, secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(APP_DIR, "sikar_service.db"))
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

SERVICES = [
    "AC रिपेयर", "प्लंबर", "इलेक्ट्रीशियन", "RO रिपेयर",
    "घर की सफाई", "पेंटिंग", "फ्रिज रिपेयर", "वॉशिंग मशीन रिपेयर"
]

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            area TEXT NOT NULL,
            address TEXT NOT NULL,
            service TEXT NOT NULL,
            preferred_date TEXT NOT NULL,
            preferred_time TEXT NOT NULL,
            notes TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'नई बुकिंग',
            created_at TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            area TEXT NOT NULL,
            experience TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'जाँच बाकी',
            created_at TEXT NOT NULL
        )""")

init_db()

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({"error": "लॉगिन आवश्यक है"}), 401
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html", services=SERVICES)

@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")

@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")

@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True) or request.form
    required = ["customer_name", "phone", "area", "address", "service", "preferred_date", "preferred_time"]
    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({"error": "कृपया सभी ज़रूरी जानकारी भरें।"}), 400
    phone = ''.join(ch for ch in str(data["phone"]) if ch.isdigit())
    if len(phone) != 10:
        return jsonify({"error": "कृपया 10 अंकों का मोबाइल नंबर डालें।"}), 400
    if data["service"] not in SERVICES:
        return jsonify({"error": "कृपया सूची में से सही सर्विस चुनें।"}), 400
    with db() as con:
        cur = con.execute("""INSERT INTO bookings
            (customer_name, phone, area, address, service, preferred_date, preferred_time, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (str(data["customer_name"]).strip()[:100], phone, str(data["area"]).strip()[:100],
             str(data["address"]).strip()[:400], str(data["service"]), str(data["preferred_date"]),
             str(data["preferred_time"]), str(data.get("notes", "")).strip()[:500],
             datetime.now().isoformat(timespec="seconds")))
        booking_id = cur.lastrowid
    return jsonify({"ok": True, "booking_id": booking_id, "message": f"बुकिंग अनुरोध #{booking_id} दर्ज हो गया है। हमारी टीम पुष्टि के लिए संपर्क करेगी।"})

@app.route("/api/partners", methods=["POST"])
def create_partner():
    data = request.get_json(silent=True) or request.form
    required = ["name", "phone", "service", "area"]
    if any(not str(data.get(k, "")).strip() for k in required):
        return jsonify({"error": "कृपया सभी ज़रूरी जानकारी भरें।"}), 400
    phone = ''.join(ch for ch in str(data["phone"]) if ch.isdigit())
    if len(phone) != 10:
        return jsonify({"error": "कृपया 10 अंकों का मोबाइल नंबर डालें।"}), 400
    if data["service"] not in SERVICES:
        return jsonify({"error": "कृपया सूची में से सही सर्विस चुनें।"}), 400
    with db() as con:
        cur = con.execute("""INSERT INTO partners (name, phone, service, area, experience, created_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (str(data["name"]).strip()[:100], phone, str(data["service"]), str(data["area"]).strip()[:100],
             str(data.get("experience", "")).strip()[:300], datetime.now().isoformat(timespec="seconds")))
        partner_id = cur.lastrowid
    return jsonify({"ok": True, "message": f"पार्टनर आवेदन #{partner_id} जमा हो गया है।"})

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if not ADMIN_PASSWORD:
            return render_template("admin.html", error="सुरक्षा के लिए सर्वर पर ADMIN_PASSWORD सेट करें।", logged_in=False)
        if request.form.get("password", "") == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        return render_template("admin.html", error="पासवर्ड सही नहीं है।", logged_in=False)
    if not session.get("admin_logged_in"):
        return render_template("admin.html", error="", logged_in=False)
    with db() as con:
        bookings = con.execute("SELECT * FROM bookings ORDER BY id DESC").fetchall()
        partners = con.execute("SELECT * FROM partners ORDER BY id DESC").fetchall()
    return render_template("admin.html", error="", logged_in=True, bookings=bookings, partners=partners)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin"))

@app.route("/api/admin/booking/<int:booking_id>", methods=["POST"])
@admin_required
def update_booking(booking_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status", "")
    allowed = ["नई बुकिंग", "पुष्टि हुई", "काम चल रहा है", "काम पूरा", "रद्द"]
    if status not in allowed:
        return jsonify({"error": "अमान्य स्टेटस"}), 400
    with db() as con:
        cur = con.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    if cur.rowcount == 0:
        return jsonify({"error": "बुकिंग नहीं मिली"}), 404
    return jsonify({"ok": True})

@app.route("/api/admin/partner/<int:partner_id>", methods=["POST"])
@admin_required
def update_partner(partner_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status", "")
    allowed = ["जाँच बाकी", "स्वीकृत", "अस्वीकृत"]
    if status not in allowed:
        return jsonify({"error": "अमान्य स्टेटस"}), 400
    with db() as con:
        cur = con.execute("UPDATE partners SET status=? WHERE id=?", (status, partner_id))
    if cur.rowcount == 0:
        return jsonify({"error": "पार्टनर नहीं मिला"}), 404
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
