from flask import render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from main import app, db
from models.models import User, Investor, Tenant, Property
from datetime import datetime
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------------------------------------User Authentication Routes----------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username is unique (you may want to enhance this)
        if User.query.filter_by(username=username).first():
            return render_template('register.html', message='Username already exists. Please choose another.')

        # Create a new user
        new_user = User(name=name, username=username, password=password)

        # Add and commit to the database
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username  # Log in the user after registration
        return redirect(url_for('home'))

    return render_template('register.html')

#<----------------- HOME ROUTES-------------------------------------------------------------------->

@app.route('/')
@login_required
def home():
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()
    return render_template('home.html', investors=investors, properties=properties, tenants=tenants)

#<------------------------------------------------INVESTORS ROUTES--------------------------------------------------------------------->

@app.route('/investors')
@login_required
def investors():
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()
    return render_template('investor.html', investors=investors, properties=properties, tenants=tenants)

@app.route('/view_investor/<investor_id>')
def view_investor(investor_id):
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()
    investor = Investor.query.get_or_404(investor_id)
    return render_template('view_investor.html', investor=investor, investors=investors, properties=properties, tenants=tenants)

@app.route('/delete_investor/<investor_id>', methods=['GET', 'POST'])
@login_required
def delete_investor(investor_id):
    investor = Investor.query.get(investor_id)

    if request.method == 'POST':
        db.session.delete(investor)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('delete_investor.html', investor=investor)

@app.route('/add_investor', methods=['GET', 'POST'])
@login_required
def add_investor():
    if request.method == 'POST':
        investor_data = {
            'id': request.form['id'],
            'name': request.form['name'],
            'user': current_user
        }
        investor_obj = Investor(**investor_data)
        db.session.add(investor_obj)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('add_investor.html')

#<----------------------------------------------PROPERTIES ROUTES--------------------------------------------------------------------->

@app.route('/add_property', methods=['GET', 'POST'])
@login_required
def add_property():
    if request.method == 'POST':
        property_data = {
            'id': request.form['property_id'],
            'building_name': request.form['building_name'],
            'unit_no': request.form['unit_no'],
            'bedrooms': int(request.form['bedrooms']),
            'square_feet': int(request.form['square_feet']),
            'price': float(request.form['price']),
            'owner_id': request.form['owner_id']
        }
        property_obj = Property(**property_data)
        db.session.add(property_obj)
        db.session.commit()
        return redirect(url_for('home'))

    investors = Investor.query.all()
    return render_template('add_property.html', investors=investors)

@app.route('/properties')
@login_required
def properties():
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()
    return render_template('properties.html', investors=investors, properties=properties, tenants=tenants)

@app.route('/view_property/<property_id>')
def view_property(property_id):
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()
    property = Property.query.get_or_404(property_id)
    return render_template('view_property.html', property=property, investors=investors, properties=properties, tenants=tenants)

#<-------------------------------------------------TENANT ROUTES----------------------------------------------------------------------->

@app.route('/tenants')
@login_required
def tenants():
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()
    return render_template('tenants.html', investors=investors, properties=properties, tenants=tenants)

@app.route('/add_tenant', methods=['GET', 'POST'])
@login_required
def add_tenant():
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()

    if request.method == 'POST':
        # Get form data
        id = request.form.get('tenant_id')
        name = request.form.get('name')
        contact_number = request.form.get('contact_number')
        email_address = request.form.get('email_address')
        passport_number = request.form.get('passport_number')
        emirates_id_number = request.form.get('emirates_id_number')
        contract_start_date = request.form.get('contract_start_date')
        contract_end_date = request.form.get('contract_end_date')
        no_of_cheques = int(request.form.get('no_of_cheques'))
        rental_amount = int(request.form.get('rental_amount'))
        security_deposit = int(request.form.get('security_deposit'))
        property_id = request.form.get('property_id')  # Assuming you have a property_id in your form
        is_current_tenant = True

        contract_start_date = datetime.strptime(contract_start_date, '%Y-%m-%d').date()
        contract_end_date = datetime.strptime(contract_end_date, '%Y-%m-%d').date()

        # Check if the property exists
        property_obj = Property.query.get(property_id)
        if not property_obj:
            return render_template('error.html', message='Property not found')

        # Create a new tenant
        new_tenant = Tenant(
            id=id,
            name=name,
            email_address=email_address,
            contact_number=contact_number,
            passport_number=passport_number,
            emirates_id_number=emirates_id_number,
            contract_start_date=contract_start_date,
            contract_end_date=contract_end_date,
            no_of_cheques=no_of_cheques,
            rental_amount=rental_amount,
            security_deposit=security_deposit,
            property=property_obj,
            is_current_tenant=is_current_tenant
        )

        # Add and commit to the database
        db.session.add(new_tenant)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add_tenant.html', investors=investors, properties=properties, tenants=tenants)

@app.route('/renew_tenant/<tenant_id>', methods=['GET', 'POST'])
def renew_tenant(tenant_id):
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()
    tenant = Tenant.query.get_or_404(tenant_id)

    if request.method == 'POST':
        # Update tenant details based on the form data
        tenant.rental_amount = request.form['new_rental_amount']
        contract_start_date = request.form['new_contract_start_date']
        contract_end_date = request.form['new_contract_end_date']

        tenant.contract_start_date = datetime.strptime(contract_start_date, '%Y-%m-%d').date()
        tenant.contract_end_date = datetime.strptime(contract_end_date, '%Y-%m-%d').date()

        # Commit the changes to the database
        db.session.commit()

        return redirect(url_for('view_tenant', tenant_id=tenant.id))

    return render_template('renew_tenant.html', tenant=tenant, investors=investors, properties=properties, tenants=tenants)

@app.route('/view_tenant/<tenant_id>')
def view_tenant(tenant_id):
    investors = Investor.query.all()
    properties = Property.query.all()
    tenants = Tenant.query.all()
    tenant = Tenant.query.get_or_404(tenant_id)
    return render_template('view_tenant.html', tenant=tenant, investors=investors, properties=properties, tenants=tenants)
