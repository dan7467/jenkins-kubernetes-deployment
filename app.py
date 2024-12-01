import os, time, hashlib
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from db_connection import db
from theirstackapi import get_payload
import datetime
from utils import parse_str_to_datetime, get_original_filename, get_user_from_db, refresh_notifications
from country_list import countries_for_language
from sys import argv

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages and session handling
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size


@app.route('/')
def home():
    refresh_notifications(session)
    return render_template('home.html')


@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    refresh_notifications(session)
    if request.method == 'POST':
    # if 'user' in session:    # TO-DO: add the check that a user is logged in, to search for jobs
        opt_params = {}
        if request.form['work_model'] == 'remote':
            opt_params['remote'] = 'true'
        if request.form['from_salary'] and request.form['to_salary']:
            opt_params['min_salary_usd'], opt_params['max_salary_usd'] = request.form['from_salary'], request.form['to_salary']
        elif request.form['from_salary'] and not request.form['to_salary']:
            opt_params['min_salary_usd'], opt_params['max_salary_usd'] = request.form['from_salary'], 2000000
        elif not request.form['from_salary'] and request.form['to_salary']:
            opt_params['min_salary_usd'], opt_params['max_salary_usd'] = 1, request.form['to_salary']
        return render_template('jobresults.html', payload=get_payload(free_text=request.form['free_text'], job_country_or_code=[request.form['country']], posted_at_max_age_days=int(request.form['posted_since']), optional_params=opt_params))
    return render_template('jobs.html', countries = dict(countries_for_language('en')))

@app.route('/about')
def about():
    refresh_notifications(session)
    return render_template('about.html')


@app.route('/logout')
def logout():
    del session['user']
    return render_template('logout.html')


@app.route('/my_profile', methods=['GET', 'POST'])
def my_profile():
    if 'user' not in session:
        flash("You must be logged in to view notifications.", "error")
        return redirect(url_for('login'))
    # TO-DO: fix the cv update / upload from my_profile page, use: cv_file = request.files['cv']
    # TO-DO: add Cover letter update / upload from my_profile page
    user = get_user_from_db(session['user'])
    refresh_notifications(session)
    if user['cv']:
        return render_template('my_profile.html', user_info = user, user_cv = get_original_filename(user['cv']))
    return render_template('my_profile.html', user_info = user)


@app.route('/notifications', methods=['GET'])
def notifications():
    if 'user' not in session:
        flash("You must be logged in to view notifications.", "error")
        return redirect(url_for('login'))

    user_email = session['user']
    
    # Fetch notifications sorted by date  
    notifications_collection = db['notifications']
    fetched_notifications = list(notifications_collection.find({"user_id": session['user']}).sort("timestamp", -1))

    notifications = sorted(fetched_notifications, key = lambda notif: parse_str_to_datetime(notif['timestamp']), reverse = True)
    
    # mark as read
    notifications_collection.update_many(
        {"user_id": user_email, "status": "unread"},  # Filter for unread notifications of this user
        {"$set": {"status": "read"}}  # Set their status to "read"
    )
    
    if len(fetched_notifications) > 100:
        ids_to_remove = [notif["_id"] for notif in notifications[100:]]
        notifications_collection.delete_many({"_id": {"$in": ids_to_remove}})

    refresh_notifications(session)
    return render_template('notifications.html', notifications=notifications)

def add_notification(user_email, title, message):
    notifications_collection = db['notifications']
    notification = {
        "user_id": user_email,
        "timestamp": datetime.datetime.now().strftime("%H:%M, %d.%m.%y"),
        "title": title,
        "message": message,
        "status": "unread"
    }
    notifications_collection.insert_one(notification)
    notifications = list(notifications_collection.find({"user_id": user_email}).sort("timestamp", -1))
    if len(notifications) > 100:
        ids_to_remove = [notif["_id"] for notif in notifications[100:]]
        notifications_collection.delete_many({"_id": {"$in": ids_to_remove}})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check Redis for user
        user = get_user_from_db(email)
        if user == -1 or user['password'] != password:
            flash('Invalid email or password!', 'error')
            time.sleep(2)
            return redirect(url_for('login'))  # TO-DO: Handle case where login is unsuccessful - raise messageBox

        # Successful login
        session['user'] = email
        session['user_firstname'] = user['full_name'].split(' ')[0]
        flash(f'Welcome back, {user['full_name']}!', 'success')
        time.sleep(2)
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        cv_file = request.files['cv']
        contact_for_future_jobs = 'No'
        if 'contact_me' in request.form:
            contact_for_future_jobs = 'Yes'
        country = request.form['country'].split(' ')
        country_code = country[0]
        country = ' '.join(country[1:])
        phone_num = request.form['phone_number']
        ALLOWED_EXTENSIONS = {'pdf', 'docx'} # for CVs

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        def allowed_email():
            return '@' in email and '.' in email and email.rindex('.') > email.rindex('@')

        if not full_name or not email or not password or not allowed_email():
            flash('Full name, email, and password are required!', 'error')
            return redirect(url_for('register'))

        # Check if email already exists
        if db["users"].find_one({"email": email}) is not None:
            flash('Email is already registered!', 'error')
            return redirect(url_for('register'))

        # Handle optional CV upload
        cv_filename = None
        if cv_file and allowed_file(cv_file.filename):
            original_filename = secure_filename(cv_file.filename)
            # Generate a unique filename if one already exists
            while True:
                file_hash = hashlib.md5(f"{original_filename}{datetime.datetime.now()}".encode()).hexdigest()[:8]
                hashed_filename = f"{original_filename.rsplit('.', 1)[0]}_{file_hash}.{original_filename.rsplit('.', 1)[1]}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], hashed_filename)
                if not os.path.exists(file_path):  # Ensure uniqueness
                    break
            # Save the file
            cv_file.save(file_path)
            cv_filename = hashed_filename
        elif cv_file:
            flash('Invalid CV format, Only PDF and DOCX are allowed.', 'error')
            return redirect(url_for('register'))
                
        # TO-DO: Linkedin API integration (when they will answer...)
        
        # TO-DO: Support dark mode
        
        user_data = {
            "full_name": full_name,
            "email": email,
            "email_verified": "No",
            "password": password,
            "cv": cv_filename or "",
            "phone": phone_num,
            "country": country,
            "country_code": country_code,
            "contact_for_future_jobs": contact_for_future_jobs
        }
        db["users"].update_one({"email": email}, {"$set": user_data}, upsert=True)
        
        if cv_filename == None:
            add_notification(email, "Complete your profile", "No CV or Resumé was uploaded, add one on 'My profile' for better experience.")
        
        add_notification(email, "Complete your profile", "Please verify your email address!")
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', countries = dict(countries_for_language('en')) )

if __name__ == '__main__':
    app.run(debug=True)