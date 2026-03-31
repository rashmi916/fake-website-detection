from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import mysql.connector
import os
import joblib
import bcrypt
import pandas as pd
from io import BytesIO
import re
import tldextract  
import requests
from PIL import Image, ImageDraw, ImageFont
import random, string, io

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ ML Model
MODEL_PATH = "D://Capstone_Project//Phishing 2.0//models_store//phishing_model_30.pkl"
model = joblib.load(MODEL_PATH)

# ✅ Feature Extraction (adjust to your dataset)
def extract_features(url: str):
    features = []
    features.append(len(url))                            # 1. URL length
    features.append(url.count("."))                      # 2. Number of dots
    features.append(1 if "@" in url else 0)              # 3. Contains '@'
    features.append(1 if "-" in url else 0)              # 4. Contains '-'
    features.append(1 if url.startswith("https") else 0) # 5. HTTPS check
    features.append(1 if re.search(r"\d", url) else 0)   # 6. Contains numbers
    features.append(1 if "login" in url.lower() else 0)  # 7. Keyword 'login'
    features.append(1 if "bank" in url.lower() else 0)   # 8. Keyword 'bank'
    features.append(1 if "secure" in url.lower() else 0) # 9. Keyword 'secure'
    features.append(1 if len(tldextract.extract(url).domain) < 5 else 0)  # 10. Short domain

    # Fill up to 30
    while len(features) < 30:
        features.append(0)
    return features

def generate_captcha_text(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ✅ DB Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="tiger",   
        database="ph_db"
    )

# ---------- AUTH ----------#
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Hash password
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        try:
            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute(
                "INSERT INTO users (username, email, password_hash, is_admin) VALUES (%s, %s, %s, %s)",
                (username, email, hashed_pw.decode("utf-8"), 0)
            )

            db.commit()
            flash("✅ Registered successfully! Please login.")
        except Exception as e:
            db.rollback()
            flash(f"❌ Registration failed: {e}")
        finally:
            db.close()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        db.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = user["is_admin"]
            flash("✅ Login successful")
            return redirect(url_for("dashboard"))
        else:
            flash("❌ Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("✅ Logged out successfully.")
    return redirect(url_for("login"))

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        # ✅ Check password match
        if new_password != confirm_password:
            flash("❌ Passwords do not match.")
            return redirect(url_for("forgot_password"))

        # ✅ Check if user exists
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        db.close()

        if not user:
            flash("❌ Email not registered.")
            return redirect(url_for("forgot_password"))

        # ✅ Hash and update new password
        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET password_hash=%s WHERE email=%s",
            (hashed_pw.decode("utf-8"), email),
        )
        db.commit()
        db.close()

        flash("✅ Password updated successfully! Please login with your new password.")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")

@app.route("/captcha")
def captcha():
    code = generate_captcha_text()
    session["captcha_code"] = code  # store in session

    # Create an image
    img = Image.new("RGB", (150, 50), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # You can use a TTF font file for nicer text
    draw.text((20, 10), code, fill=(0, 0, 0))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return send_file(buffer, mimetype="image/png")



# ---------- USER DASHBOARD ----------
@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

# ---------- URL CHECK ----------
@app.route("/check", methods=["GET", "POST"])
def check():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        url = request.form["url"]
        captcha_input = request.form["captcha_input"]

        # Validate captcha
        if captcha_input != session.get("captcha_code"):
            flash("❌ Invalid CAPTCHA, try again.")
            return redirect(url_for("check"))

        # --- Feature extraction & prediction ---
        features = extract_features(url)

        # Prediction
        prediction = model.predict([features])[0]
        verdict = "Phishing" if prediction == 1 else "Safe"

        # Probability score (if model supports predict_proba)
        try:
            proba = model.predict_proba([features])[0][1]  # probability of phishing
        except AttributeError:
            proba = float(prediction)  # fallback: just 0/1

        # Convert features list into string for storage
        features_str = ",".join(map(str, features))

        # ✅ Save to DB
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO checks (user_id, url, verdict, score, features, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
            (session["user_id"], url, verdict, proba, features_str),
        )
        db.commit()
        db.close()

        return render_template("result.html", url=url, verdict=verdict, score=proba)

    return render_template("check.html")



# ---------- HISTORY ----------
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM checks WHERE user_id=%s ORDER BY created_at DESC", (session["user_id"],))
    checks = cursor.fetchall()
    db.close()
    return render_template("history.html", checks=checks)

# ---------- REPORTING ----------
@app.route("/report")
def report():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT verdict, COUNT(*) as cnt FROM checks WHERE user_id=%s GROUP BY verdict", (session["user_id"],))
    data = cursor.fetchall()
    db.close()

    labels = [row["verdict"] for row in data]
    counts = [row["cnt"] for row in data]
    return render_template("report.html", labels=labels, counts=counts)

@app.route("/export")
def export():
    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM checks WHERE user_id=%s", (session["user_id"],))
    rows = cursor.fetchall()
    db.close()

    df = pd.DataFrame(rows)
    csv_data = df.to_csv(index=False).encode("utf-8")
    buffer = BytesIO(csv_data)
    buffer.seek(0)

    return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="history.csv")

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("feedback")  # <- in template, textarea name="feedback"

        if not name or not email or not message:
            flash("❌ Please fill all fields.")
            return redirect(url_for("dashboard"))

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO feedback (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message)
        )
        db.commit()
        db.close()

        flash("✅ Thank you for your feedback!")
        return redirect(url_for("dashboard"))

    return render_template("feedback.html")


# ---------- ADMIN ----------
@app.route("/admin")
def admin_panel():
    if "user_id" not in session or not session.get("is_admin"):
        flash("❌ Unauthorized.")
        return redirect(url_for("dashboard"))
    return render_template("admin.html")

@app.route("/dataset/upload", methods=["GET", "POST"])
def dataset_upload():
    if "user_id" not in session or not session.get("is_admin"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        file = request.files["dataset"]
        path = os.path.join("uploads", file.filename)
        file.save(path)

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO datasets (name, file_path, uploaded_by) VALUES (%s,%s,%s)",
            (file.filename, path, session["user_id"])
        )
        db.commit()
        db.close()
        flash("✅ Dataset uploaded successfully")
        return redirect(url_for("admin_panel"))
    return render_template("dataset_upload.html")

@app.route("/admin/users")
def view_users():
    if "user_id" not in session or not session.get("is_admin"):
        flash("❌ Unauthorized.")
        return redirect(url_for("dashboard"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, is_admin, created_at FROM users")
    users = cursor.fetchall()
    db.close()

    return render_template("view_users.html", users=users)

@app.route("/admin/checks")
def view_checks():
    if "user_id" not in session or not session.get("is_admin"):
        flash("❌ Unauthorized.")
        return redirect(url_for("dashboard"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM checks ORDER BY created_at DESC")
    checks = cursor.fetchall()
    db.close()

    return render_template("view_checks.html", checks=checks)
@app.route("/genhash")
def genhash():
    password = "admin123".encode("utf-8")
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed.decode()


# ---------- API ----------
@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.json
    url = data.get("url")

    features = extract_features(url)
    prediction = model.predict([features])[0]
    verdict = "Phishing" if prediction == 1 else "Safe"

    return jsonify({"url": url, "verdict": verdict})

# ---------- MAIN ----------
if __name__ == "__main__":
    app.run(debug=True)
