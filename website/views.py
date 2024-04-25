from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from .processing import main

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    #retrieve the csv data if any from user
    csv_data = current_user.csv_data
    return render_template("home.html.j2", csv_data=csv_data)

@views.route('/home/estimations', methods=['POST'])
@login_required
def homeEstimaitons():
    date = request.form['date']

    if not date:
        flash('Please ensure you select a date', category='error')
        return redirect(url_for('views.home'))
    
    csv_data = current_user.csv_data

    if not csv_data:
        flash('Please ensure you have uploaded a CSV Data file', category='error')
        return redirect(url_for('views.home'))
    
    output_devices, power_output, date = main(date)
    return render_template("home.html.j2", csv_data=csv_data, output_devices=output_devices, power_output = power_output, date=date)

@views.route('/preferences')
@login_required
def preferences():
    return render_template("preferences.html.j2")

@views.route('/howto', methods=['POST'])
@login_required
def howto():
    return render_template("howto.html.j2")

@views.route('/devices')
@login_required
def devices():
    devices = current_user.devices
    return render_template("devices.html.j2", devices=devices) #pass in devies to load any existing devices from user