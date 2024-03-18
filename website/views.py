from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_login import login_required, current_user
from .processing import processingMain


views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    #retrieve the csv data if any from user
    csv_data = current_user.csv_data
    processingOutput = processingMain()
    return render_template("home.html", csv_data=csv_data, processingOutput = processingOutput)

@views.route('/preferences')
@login_required
def preferences():
    return render_template("preferences.html")

@views.route('/howto', methods=['POST'])
@login_required
def howto():
    return render_template("howto.html")

@views.route('/getUserData')
@login_required
def getUserData():
    devices = current_user.devices
    return render_template("getUserData.html", devices=devices) #pass in devies to load any existing devices from user


