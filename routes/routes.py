from flask import flash, render_template, request, redirect, url_for, session
import os
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from main import app, db
from models.models import User, Investor, Tenant, Property, Cheque
from datetime import datetime
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.template_filter('format_number')
def format_number(value):
    if value is None:
        return "0"
    return f"{int(value):,}"

@app.template_filter('format_date')
def format_date(date):
    return date.strftime('%d/%m/%Y')
# ----------------------------------------User Authentication Routes----------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out', 'info')
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
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('register.html', message='Username already exists. Please choose another.')

        # Create a new user
        new_user = User(name=name, username=username, password=password)

        # Add and commit to the database
        db.session.add(new_user)
        db.session.commit()

        session['username'] = username  # Log in the user after registration
        flash('Registration successful. Welcome!', 'success')
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

from flask import flash, redirect, url_for

@app.route('/upload_file/<entity_type>/<entity_id>', methods=['POST'])
@login_required
def upload_file(entity_type, entity_id):
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.referrer)

    file = request.files['file']
    custom_filename = request.form.get('filename', '')
    file_tag = request.form['file_tag']

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.referrer)

    if file and allowed_file(file.filename):
        entity_type = entity_type.lower()
        base_path = app.config['UPLOAD_FOLDER']

        new_filename = custom_filename if custom_filename else file.filename

        # Determine the correct folder path based on entity type and hierarchy
        if entity_type == 'property':
            property_obj = Property.query.get(entity_id)
            if not property_obj:
                flash('Property not found', 'danger')
                return redirect(request.referrer)

            investor_id = property_obj.owner_id
            upload_folder = os.path.join(base_path, current_user.name, f'{investor_id}', f'{entity_id}', file_tag)
        
        elif entity_type == 'tenant':
            tenant_obj = Tenant.query.get(entity_id)
            if not tenant_obj:
                flash('Tenant not found', 'danger')
                return redirect(request.referrer)

            property_id = tenant_obj.property_id
            property_obj = Property.query.get(property_id)
            if not property_obj:
                flash('Property for tenant not found', 'danger')
                return redirect(request.referrer)

            investor_id = property_obj.owner_id
            upload_folder = os.path.join(base_path, current_user.name, f'{investor_id}', f'{property_id}', f'{entity_id}', file_tag)
        
        elif entity_type == 'investor':
            upload_folder = os.path.join(base_path, current_user.name, f'{entity_id}', file_tag)
        
        else:
            flash('Invalid entity type', 'danger')
            return redirect(request.referrer)

        os.makedirs(upload_folder, exist_ok=True)

        # Save the file
        filename = os.path.join(upload_folder, new_filename)
        file.save(filename)

        # Optional: Save the file path in the database
        # db.session.commit()

        flash('File uploaded successfully!', 'success')
        return redirect(request.referrer)
    
    flash('Invalid file type', 'danger')
    return redirect(request.referrer)


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
    today = datetime.today().date() 
    return render_template('tenants.html', investors=investors, properties=properties, tenants=tenants, today=today)

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

                # Get the cheques data from the form
        cheques_data = request.form.getlist('cheques[0][cheque_number]')
        cheque_amounts = request.form.getlist('cheques[0][amount]')
        cheque_due_dates = request.form.getlist('cheques[0][due_date]')

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

                # Add the cheques to the database
        for i in range(no_of_cheques):
            cheque_number = cheques_data[i]
            amount = cheque_amounts[i]
            due_date = datetime.strptime(cheque_due_dates[i], '%Y-%m-%d').date()

            # Create a new Cheque object
            new_cheque = Cheque(
                cheque_number=cheque_number,
                amount=amount,
                due_date=due_date,
                tenant_id=new_tenant.id
            )

            # Add and commit cheque data
            db.session.add(new_cheque)
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
    # Fetch the property associated with the tenant
    property = Property.query.filter_by(id=tenant.property_id).first()  # Adjust `property_id` field name as per your model

    # Fetch the investor associated with the property
    investor = Investor.query.filter_by(id=property.owner_id).first() 
    today = datetime.today().date()
    return render_template('view_tenant.html', tenant=tenant, investor=investor, property=property, tenants=tenants, today=today)
