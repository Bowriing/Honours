from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .models import CSVData


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.password:
            if check_password_hash(user.password, password):
                flash('Logged In Successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('Email does not exist', category='error')
            
    return render_template('login.html')
                
@auth.route('/logout')
@login_required #cannot be accessed unless logged in
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
            return redirect(url_for('auth.sign_up'))

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, firstName=firstName, password=generate_password_hash(password1, method='pbkdf2:sha256'))#save password using hashing (sha256 method cam from tutorial)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account Successfully Created.', category='success')
            return redirect(url_for('views.home'))
            
    return render_template("sign-up.html")

#CSV FUNCTIONS
@auth.route('upload-csv', methods = ['POST'])
def upload_csv():
    if 'csv_file' not in request.files:
        flash('No file to upload', category='error')
        return redirect(url_for('views.home'))
    
    csv_file = request.files['csv_file']

    #verification of file
    if csv_file.filename == '':
        flash('No selected file', category='error')
        return redirect(url_for('views.home'))
    
    if not csv_file.filename.endswith('.csv'):
        flash('Invalid file format, please upload a csv file', category='error')
        return redirect(url_for('views.home'))
    
    #read the csv file for upload
    csv_content = csv_file.read().decode('utf-8')

    #upload data to users account in database
    if current_user.csv_data:
        current_user.csv_data.csv_content = csv_content #set data to user data field/update no append

    #if an existing csvdate field is not there then create a new one with associated to signed in user on the database
    else:
        new_csv_data = CSVData(csv_content=csv_content, user_id=current_user.id)
        current_user.csv_data = new_csv_data

    #upload changes/updates to the sql database
    db.session.commit()


    flash('Successfully uploaded CSV', category='success')
    return redirect(url_for('views.home'))
