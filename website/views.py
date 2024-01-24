from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    #retrieve the csv data if any from user
    csv_data = current_user.csv_data
    return render_template("home.html", csv_data=csv_data)

 