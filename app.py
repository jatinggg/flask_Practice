from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

# Load env vars (Local development support)
# In production/staging, these are injected by the Github Action script into the .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = os.getenv("SECRET_KEY")

mongo = PyMongo(app)

# -------------------------------------------------------------------
# CI/CD & Deployment Routes
# -------------------------------------------------------------------

@app.route('/health')
def health_check():
    """
    Simple route for AWS or CI/CD pipelines to check if the app is up.
    Returns JSON 200 OK.
    """
    return jsonify({"status": "success", "message": "Application is running"}), 200

# -------------------------------------------------------------------
# Application Logic
# -------------------------------------------------------------------

# Home page -> list students
@app.route('/')
def index():
    # Defensive programming: Handle case where DB might be empty or connection fails gracefully
    try:
        students = mongo.db.students.find()
        return render_template('index.html', students=students)
    except Exception as e:
        return f"Error connecting to database: {e}", 500

# Add student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        mongo.db.students.insert_one({
            "name": name,
            "email": email,
            "course": course
        })
        return redirect(url_for('index'))
    return render_template('add_student.html')

# Update student
@app.route('/update/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    student = mongo.db.students.find_one({"_id": ObjectId(student_id)})
    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']
        new_course = request.form['course']
        mongo.db.students.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"name": new_name, "email": new_email, "course": new_course}}
        )
        return redirect(url_for('index'))
    return render_template('update_student.html', student=student)

# Delete student
@app.route('/delete/<student_id>')
def delete_student(student_id):
    mongo.db.students.delete_one({"_id": ObjectId(student_id)})
    return redirect(url_for('index'))

# -------------------------------------------------------------------
# Main Entry Point
# -------------------------------------------------------------------

if __name__ == '__main__':
    # This block is ONLY executed when you run `python app.py` locally.
    # When deployed on EC2, Gunicorn imports 'app' directly and ignores this block.
    app.run(debug=True, port=8000)
