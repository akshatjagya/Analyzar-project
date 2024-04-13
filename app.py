import os
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import psycopg2
from openai import OpenAI

app = Flask(__name__)
app.config['SECRET_KEY'] = '1223Akshat'
app.config['UPLOAD_FOLDER'] = 'uploads/'

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

# Define the allowed_file function
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database connection details
connection_config = {
    'dsn': "postgres://analyzar_db_e8ou_user:oNSbiWJurpryUxZNIjjorWwUJPq4I0e4@dpg-co7ek8cf7o1s73cm96rg-a.singapore-postgres.render.com/analyzar_db_e8ou"
}

# Initialize OpenAI client
openai_client = OpenAI(api_key="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")

# Generate unique code
def generate_unique_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(10))

# Process OCR using pytesseract
def process_ocr(filename):
    image = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    text = pytesseract.image_to_string(image).lower()
    return text

# Extract purchase info using OpenAI
def extract_purchase_info(ocr_text):
    prompt = f"""Extract the following information from the OCR text:

    Title: (name of what item purchased from where like food from dominos, sony camera, electricity bill, ola/uber/auto cab, stationery from walmart, grocery from raj-mandir, etc),
    Platform: (online/offline),
    Date (in dd-mm-yyyy format example 08-04-2024),
    Time (in hh:mm am/pm format example 06:31 PM)(return NA if not available),
    Place/City (check if such city exists, return only city or state),
    Total Amount (return total amount only, example if ₹4000 then return 4000 or 200$ then return 200).
    Predict with accuracy a Category from these 10 choices only: Food, Travel & Transportation, Shopping, Home Utilities, Entertainment, Health & Wellness, Education, Personal Care, Insurance & Taxes. 
    OCR Text:
    \"{ocr_text}\"
    """

    response = openai_client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=200,
    )

    result_text = response.choices[0].text.strip()

    # Split the response into lines and extract relevant information
    lines = result_text.split("\n")

    # Set default values
    title = platform = date = time = place_city = total_amount = category = "Not found"

    for line in lines:
        if "Title:" in line:
            title = line.split(": ")[1]
        elif "Platform:" in line:
            platform = line.split(": ")[1]
        elif "Date" in line:
            date = line.split(": ")[1]
        elif "Time" in line:
            time = line.split(": ")[1]
        elif "Place/City" in line:
            place_city = line.split(": ")[1]
        elif "Total Amount" in line:
            total_amount = line.split(": ")[1]
        elif "Category" in line:
            category = line.split(": ")[1]

    return title, platform, date, time, place_city, total_amount, category

# Save invoice data to database
from datetime import datetime

def remove_currency_symbol(total_amount):
    # Define a list of common currency symbols
    currency_symbols = ['$', '€', '£', '¥', '₹']

    # Remove currency symbols from the total_amount string
    for symbol in currency_symbols:
        total_amount = total_amount.replace(symbol, '')

    # Remove any non-numeric characters
    total_amount = ''.join(filter(str.isdigit, total_amount))

    return total_amount

def save_invoice_data(invoice_data, user_id):
    connection = psycopg2.connect(**connection_config)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO invoice_details (title, platform, transaction_date, transaction_time, place, total_cost, category, unique_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            # Remove any extra whitespace from the date string before parsing
            transaction_date_str = invoice_data[2].strip()

            # Convert date string to datetime object
            transaction_date = datetime.strptime(transaction_date_str, '%d-%m-%Y').date()

            # Format time data or set default if not available
            if invoice_data[3] != 'NA':
                transaction_time = datetime.strptime(invoice_data[3], '%I:%M %p').strftime('%I:%M %p')
            else:
                transaction_time = '12:00 AM'  # Default time value when not available

            # Remove currency symbol from total_amount and convert to integer
            total_cost = int(remove_currency_symbol(invoice_data[5]))

            cursor.execute(sql, (invoice_data[0], invoice_data[1], transaction_date, transaction_time, invoice_data[4], total_cost, invoice_data[6], user_id))
        connection.commit()
    finally:
        connection.close()


def login_user(email, provided_unique_code):
    connection = psycopg2.connect(**connection_config)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT unique_code FROM user_details WHERE email = %s AND unique_code = %s"
            cursor.execute(sql, (email, provided_unique_code))
            retrieved_unique_code = cursor.fetchone()
            if retrieved_unique_code:
                session['unique_code'] = retrieved_unique_code[0]
                return retrieved_unique_code[0]  # Return the unique code
            else:
                return None
    finally:
        connection.close()


# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        # Check if email already exists
        connection = psycopg2.connect(**connection_config)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM public.user_details WHERE email = %s"
                cursor.execute(sql, (email,))
                existing_user = cursor.fetchone()

            if existing_user:
                return render_template('register.html', error='Email already exists. Please enter a new email.')
        finally:
            connection.close()

        unique_code = generate_unique_code()

        # Save user details to database
        connection = psycopg2.connect(**connection_config)
        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO public.user_details(name, email, unique_code) VALUES (%s, %s, %s)"
                cursor.execute(sql, (name, email, unique_code))
            connection.commit()
        finally:
            connection.close()

        return render_template('register.html', unique_code=unique_code, success=True)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Initialize error variable
    
    if request.method == 'POST':
        email = request.form['email']
        unique_code = request.form['unique_code']
        
        # Check if the email and unique code pair exist in the database
        retrieved_user_id = login_user(email, unique_code)  # Retrieve the user_id
        if retrieved_user_id:
            session['user_id'] = retrieved_user_id
            return redirect(url_for('upload_invoice'))
        else:
            error = 'Invalid email or unique code.'
    
    # Pass error to the template
    return render_template('login.html', error=error)


@app.route('/upload_invoice', methods=['GET', 'POST'])
def upload_invoice():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        uploaded_files = request.files.getlist('invoice[]')  # Change to 'invoice[]'
        errors = []

        for uploaded_file in uploaded_files:
            if uploaded_file.filename == '':
                errors.append('No file selected.')
                continue

            if uploaded_file and allowed_file(uploaded_file.filename):
                filename = secure_filename(uploaded_file.filename)
                try:
                    uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                except Exception as e:
                    errors.append(f'Error saving file: {str(e)}')
                    continue

                # Process OCR and extract data
                ocr_text = process_ocr(filename)
                invoice_data = extract_purchase_info(ocr_text)
                # Save invoice data to database
                save_invoice_data(invoice_data, session['user_id'])
            else:
                errors.append('Invalid file format. Please upload an image file.')

        if errors:
            return render_template('upload_invoice.html', errors=errors)
        else:
            return 'Invoices uploaded successfully'

    return render_template('upload_invoice.html')

if __name__ == '__main__':
    app.run(debug=True)
