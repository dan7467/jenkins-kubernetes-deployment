from datetime import datetime
from db_connection import db
import re

def refresh_notifications(session):
    if 'user' in session:
        # notifications_key = f"notifications:{session['user']}"
        # Fetch notifications for the logged-in user, from redis
        # user_notifications = db.lrange(notifications_key, 0, -1)
        notifications = list(db['notifications'].find({"user_id": session['user']}).sort("timestamp", -1))
        unread_notifications = list(filter(lambda notif: notif['status'] == 'unread', notifications))
        session['unread_notifications'] = len(unread_notifications)


def parse_str_to_datetime(x):
    # trim spaces from end
    i = len(x) - 1
    while x[i] == ' ':
        i -= 1
    i += 1
    return datetime.strptime(x[:i], "%H:%M, %d.%m.%y")


def get_original_filename(hashed_filename):  # To extract original filename without the hash
    match = re.match(r"^(.*)_\w{8}\.(\w+)$", hashed_filename)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    return hashed_filename  # Return the hashed filename if no match


def get_user_from_db(email):
    # user = db.hgetall(f"user:{email}")
    user = db["users"].find_one({"email": email})
    if user:
        return user
    return -1