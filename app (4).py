from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Response
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from bson.json_util import dumps
from bson import ObjectId
import time, os , requests, threading, pytz
from werkzeug.utils import secure_filename
from bson.int64 import Int64 
from functools import wraps
import cv2


app = Flask(__name__)
app.secret_key = 'garlicgreenhouse123'
bcrypt = Bcrypt(app)
serializer = URLSafeTimedSerializer(app.secret_key)
UPLOAD_FOLDER = 'static/profilepics'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

INVITE_CODE = "G49glis12!3#"
ESP32_IP_ADDRESS = "http://192.168.1.18:80"
ESP32_IP_ADDRESS2 = "http://10.40.5.35:80"
esp32_url = "http://192.168.1.63:80" 
ac_ip = "192.168.1.18" 
num_relays = 4
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# MQTT broker configuration
mqtt_broker = "broker.hivemq.com"  
temperature_topic = "garlicgreenhouse/temperature"
humidity_topic = "garlicgreenhouse/humidity"
mqttLumens1Topic = "garlicgreenhouse/light1"
mqttLumens2Topic = "garlicgreenhouse/light2"
mqttLumens3Topic = "garlicgreenhouse/light3"
mqttLumens4Topic = "garlicgreenhouse/light4"
current_temperature_topic = "garlicgreenhouse/current_temperature"
LED_CONTROL_TOPIC1 = "garlicgreenhouse/rack1state"
LED_CONTROL_TOPIC2 = "garlicgreenhouse/rack2state"
LED_CONTROL_TOPIC3 = "garlicgreenhouse/rack3state"
LED_CONTROL_TOPIC4 = "garlicgreenhouse/rack4state"
AC_CONTROL_TOPIC ="garlicgreenhouse/ac_state"

# MongoDB configuration
mongo_client = MongoClient("mongodb+srv://iotgarlic:garlicgreenhouse2023@garlicgreenhouse.s6eknyu.mongodb.net")
mongodb_db = mongo_client.GarlicGreenhouse
light_state_collection = mongodb_db.light_state
schedule_collection = mongodb_db.schedule
light_toggle_collection = mongodb_db.light_toggle
ac_control_collection = mongodb_db.ac_control
users_collection = mongodb_db.users

sensor_data = {
    "temperature": None,
    "humidity": None,
    "lumens1": None,
    "lumens2": None,
    "lumens3": None,
    "lumens4": None,
    "current_temp": None
}

# MQTT client configuration
client = mqtt.Client()
data_lock = threading.Lock()
insert_interval = 300  

# MQTT client configuration
client = mqtt.Client()
manila_timezone = pytz.timezone('Asia/Manila')

def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")

    try:
        payload = float(payload)
    except ValueError:
        payload = None

    with data_lock:
        if topic == temperature_topic:
            sensor_data["temperature"] = payload
        elif topic == humidity_topic:
            sensor_data["humidity"] = payload
        elif topic == mqttLumens1Topic:
            sensor_data["lumens1"] = payload
        elif topic == mqttLumens2Topic:
            sensor_data["lumens2"] = payload
        elif topic == mqttLumens3Topic:
            sensor_data["lumens3"] = payload
        elif topic == mqttLumens4Topic:
            sensor_data["lumens4"] = payload
        elif topic == current_temperature_topic:
            sensor_data["current_temp"] = payload
        elif topic == AC_CONTROL_TOPIC:
            handle_ac_control(payload) 
        elif topic in [LED_CONTROL_TOPIC1, LED_CONTROL_TOPIC2, LED_CONTROL_TOPIC3, LED_CONTROL_TOPIC4]:
            handle_led_control(topic, payload)

def handle_ac_control(current_temperature):
    # Make sure the current_temperature is within the desired range
    if 17.0 <= current_temperature <= 30.0:
        # Craft the URL with the ESP32 IP and the current temperature
        url = f"http://{ac_ip}/set?temp={int(current_temperature)}"
        try:
            # Send the HTTP GET request
            response = requests.get(url)
            if response.status_code == 200:
                print("HTTP request sent successfully:", url)
            else:
                print("Failed to send HTTP request:", response.status_code)
        except Exception as e:
            print("Error while sending HTTP request:", str(e))
    else:
        print("Temperature out of range for AC control")

def handle_led_control(topic, payload):
    if payload is not None:
        # Extract relay number from the topic
        relay_num = int(topic.split('/')[-1].replace('rack', '').replace('state', ''))

        # Print the received payload
        print("Received payload:", payload)

        # Convert payload to an integer without decimal point
        payload_int = int(float(payload))

        # Call the appropriate relay control endpoint based on the payload
        esp32_ip_address = ESP32_IP_ADDRESS if relay_num <= 2 else ESP32_IP_ADDRESS2
        if payload_int == 1:
            response = requests.get(f'{esp32_ip_address}/turn_on/{relay_num}')
            if response.status_code == 200:
                return f"Relay {relay_num} turned on successfully"
            else:
                return f"Failed to turn on relay {relay_num}. Status code: {response.status_code}"
        elif payload_int == 0:
            response = requests.get(f'{esp32_ip_address}/turn_off/{relay_num}')
            if response.status_code == 200:
                return f"Relay {relay_num} turned off successfully"
            else:
                return f"Failed to turn off relay {relay_num}. Status code: {response.status_code}"
        else:
            print("Invalid payload for relay control")
            return
    else:
        print("Empty payload received for topic:", topic)

def insert_data_into_mongodb():
    last_inserted_data = None  # Store the last inserted data

    while True:
        time.sleep(insert_interval)
        with data_lock:
            # Check if there is new data
            if any(value is not None for value in sensor_data.values()):
                # Get the current time in Asia/Manila timezone
                current_time_manila = datetime.now(manila_timezone)

                # Format the time and date in 12-hour format
                formatted_time = current_time_manila.strftime('%I:%M:%S %p')
                formatted_date = current_time_manila.strftime('%Y-%m-%d')

                combined_data = {
                    "temperature": sensor_data["temperature"],
                    "humidity": sensor_data["humidity"],
                    "lumens1": sensor_data["lumens1"],
                    "lumens2": sensor_data["lumens2"],
                    "lumens3": sensor_data["lumens3"],
                    "lumens4": sensor_data["lumens4"],
                    "time": formatted_time,
                    "date": formatted_date
                }

                # Insert a single document containing temperature, humidity, and lumens data
                mongodb_db.sensor_data.insert_one(combined_data)

                # Update the last inserted data
                last_inserted_data = combined_data

                print("Data inserted into MongoDB")
            elif last_inserted_data is not None:
                # Insert the last known data if no new data is available
                mongodb_db.sensor_data.insert_one(last_inserted_data)
                print("No new data. Inserting last known data into MongoDB")

# Start the thread for data insertion
insert_thread = threading.Thread(target=insert_data_into_mongodb)
insert_thread.daemon = True
insert_thread.start()

# Routes for retrieving sensor data
@app.route('/publish_sensor_data', methods=['GET', 'POST'])
def publish_sensor_data():
    with data_lock:
        # Return the latest sensor data including all lumens topics
        return jsonify({
            "temperature": sensor_data["temperature"],
            "humidity": sensor_data["humidity"],
            "lumens1": sensor_data["lumens1"],
            "lumens2": sensor_data["lumens2"],
            "lumens3": sensor_data["lumens3"],
            "lumens4": sensor_data["lumens4"]
        })


@app.route('/publish-mqtt', methods=['GET'])
def publish_mqtt():
    topic = request.args.get('topic')
    message = request.args.get('message')

    # Publish to MQTT
    client.publish(topic, message)

    return jsonify({'success': True, 'topic': topic, 'message': message})

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/open_me')
def open_me():
    return render_template('open_me.html')

@app.route('/about')
def about():
    return render_template('about.html', sensor_data=sensor_data, num_relays=num_relays)



@app.route('/alerts')
def alerts():
    # Fetch all schedule data from MongoDB and sort it in ascending order based on MonthYearSelected and time_start
    schedule_data = mongodb_db.schedule.find().sort([("year", 1), ("month", 1), ("day", 1), ("time_start", 1)])

    # Convert MongoDB cursor to a list of dictionaries
    schedule_list = [entry for entry in schedule_data]

    return render_template('alerts.html',sensor_data=sensor_data, num_relays=num_relays,schedule_list=schedule_list)

@app.route('/reminders')
def reminders():
    # Fetch schedule data from MongoDB and sort it in ascending order based on MonthYearSelected and time_start
    schedule_data = mongodb_db.schedule.find().sort([("monthYearSelected", 1), ("time_start", 1)])

    # Convert MongoDB cursor to a list of dictionaries
    schedule_list = [entry for entry in schedule_data]

    return render_template('alerts.html', schedule_list=schedule_list)

@app.route('/get_schedule_data', methods=['GET'])
def get_schedule_data():
    # Fetch schedule data from MongoDB and return it as JSON
    schedule_data = mongodb_db.schedule.find({}, {'_id': 0})
    return jsonify(list(schedule_data))

@app.route('/charts')
def charts():
    return render_template('charts.html', sensor_data=sensor_data, num_relays=num_relays)
        
@app.route('/get_temperature_data_for_date/<date>', methods=['GET'])
def get_temperature_data_for_date(date):
    # Assuming you have a MongoDB collection named 'sensor_data'
    # Change 'sensor_data' to the actual name of your collection
    temperature_data = mongodb_db.sensor_data.find(
        {'date': date},
        {'_id': 0, 'time': 1, 'temperature': 1}
    ).sort('time')

    # Convert MongoDB cursor to a list of dictionaries
    temperature_list = [entry for entry in temperature_data]

    return jsonify(temperature_list)

@app.route('/get_humidity_data_for_date/<date>', methods=['GET'])
def get_humidity_data_for_date(date):
    humidity_data = mongodb_db.sensor_data.find(
        {'date': date},
        {'_id': 0, 'time': 1, 'humidity': 1}
    ).sort('time')

    humidity_list = [entry for entry in humidity_data]

    return jsonify(humidity_list)

@app.route('/get_lumens1_data_for_date/<date>', methods=['GET'])
def get_lumens1_data_for_date(date):
    lumens1_data = mongodb_db.sensor_data.find(
        {'date': date},
        {'_id': 0, 'time': 1, 'lumens1': 1}
    ).sort('time')

    lumens1_list = [entry for entry in lumens1_data]

    return jsonify(lumens1_list)

@app.route('/get_lumens2_data_for_date/<date>', methods=['GET'])
def get_lumens2_data_for_date(date):
    lumens2_data = mongodb_db.sensor_data.find(
        {'date': date},
        {'_id': 0, 'time': 1, 'lumens2': 1}
    ).sort('time')

    lumens2_list = [entry for entry in lumens2_data]

    return jsonify(lumens2_list)

@app.route('/get_lumens3_data_for_date/<date>', methods=['GET'])
def get_lumens3_data_for_date(date):
    lumens3_data = mongodb_db.sensor_data.find(
        {'date': date},
        {'_id': 0, 'time': 1, 'lumens3': 1}
    ).sort('time')

    lumens3_list = [entry for entry in lumens3_data]

    return jsonify(lumens3_list)

@app.route('/get_lumens4_data_for_date/<date>', methods=['GET'])
def get_lumens4_data_for_date(date):
    lumens4_data = mongodb_db.sensor_data.find(
        {'date': date},
        {'_id': 0, 'time': 1, 'lumens4': 1}
    ).sort('time')

    lumens4_list = [entry for entry in lumens4_data]

    return jsonify(lumens4_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        invite_code = request.form.get('inv_code')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the invite code is valid
        if invite_code != INVITE_CODE:
            error_message = "Invalid invite code. Please try again."
            return render_template('register.html', error_message=error_message)

        # Check if the email is already registered
        existing_user = mongodb_db.users.find_one({"email": email})
        if existing_user:
            error_message = "Email already registered. Please use a different email."
            return render_template('register.html', error_message=error_message)

        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Store the user data in MongoDB
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "registration_date": datetime.now()
        }
        mongodb_db.users.insert_one(user_data)

        # Redirect to the login page or another relevant page after successful registration
        return redirect(url_for('main_login'))

    # If it's a GET request, render the registration template
    return render_template('register.html')

@app.route('/get_invite_code')
def get_invite_code():
    return jsonify({'invite_code': INVITE_CODE})

@app.route('/users')
def users():
    # Assuming you have a MongoDB collection named 'users'
    user = mongodb_db.users.find_one({"email": session.get('email')})
    filename = user.get('filename', 'Prof_placeH.png')  # Get the filename from the user document, or use a default value
    
    return render_template('users.html', sensor_data=sensor_data, num_relays=num_relays, filename=filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save the uploaded file to the upload folder
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Save the filename in the database
            if 'email' in session:
                email = session['email']
                mongodb_db.users.update_one({"email": email}, {"$set": {"filename": filename}})
            
            return 'Image uploaded successfully'

@app.route('/update_user', methods=['POST'])
def update_user():
    if 'email' in session:
        email = session['email']
        user = mongodb_db.users.find_one({"email": email})

        if user and bcrypt.check_password_hash(user.get('password', ''), request.form['old_password']):
            # Update user data in the database
            update_data = {"name": request.form['fname'], "email": request.form['email']}

            # Check if the "Change Password" checkbox is selected
            if request.form.get('change_password'):
                old_password = request.form['old_password']
                new_password = request.form['new_password']

                # Verify that the old password matches the one in the database
                if not bcrypt.check_password_hash(user.get('password', ''), old_password):
                    error_message = "Invalid old password. Please try again."
                    return render_template('users.html', error_message=error_message)

                # Hash and update the new password
                update_data['password'] = bcrypt.generate_password_hash(new_password).decode('utf-8')

            mongodb_db.users.update_one({"email": email}, {"$set": update_data})

            # Redirect to the index route on successful update
            return redirect(url_for('main_login'))
        else:
            error_message = "Invalid credentials. Please try again."
            return render_template('users.html', error_message=error_message)
    else:
        # Redirect to the login page if the user is not logged in
        return redirect(url_for('login'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/main_login')
def main_login():
    return render_template('main_login.html') 

@app.route('/front')
def front():
    return render_template('front.html')    

@app.route('/change_password')
def change_password():
    return render_template('change_password.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # If the request is made with JSON data
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            # If the request is made with form data (HTML form submission)
            email = request.form.get('email')
            password = request.form.get('password')

        # Check if email matches a user in the MongoDB collection
        user = mongodb_db.users.find_one({"email": email})

        if user and bcrypt.check_password_hash(user.get('password', ''), password):
            # Store user ID, email, and name in the session
            session['user_id'] = str(user.get('_id'))
            session['email'] = email
            session['name'] = user.get('name')

            # Perform login logic if needed
            if request.is_json:
                return jsonify({'success': True})
            else:
                # Redirect to the index route on successful login
                return redirect(url_for('front'))
        else:
            error_message = "Invalid email or password. Please try again."

            if request.is_json:
                return jsonify({'success': False, 'message': error_message})
            else:
                # Render the login template with the error message
                return render_template('main_login', error_message=error_message)

    # If it's a GET request, render the login template
    return render_template('login.html')

@app.route('/')
def default():
    # Redirect to the /login route
    return redirect(url_for('main_login'))

@app.route('/turn_on/<int:relay_num>')
def turn_on(relay_num):
    if 1 <= relay_num <= num_relays:
        try:
            # Choose the appropriate ESP32 IP address based on relay number
            esp32_ip_address = ESP32_IP_ADDRESS if relay_num <= 2 else ESP32_IP_ADDRESS2
            response = requests.get(f'{esp32_ip_address}/turn_on/{relay_num}')
            
            if response.status_code == 200:
                # Update the relay state in MongoDB
                light_state_collection.update_one(
                    {'relay_num': relay_num},
                    {'$set': {'state': True}},
                    upsert=True  # Create a new document if it doesn't exist
                )
                
                # Get user's name from the session email
                name = None
                if 'email' in session:
                    email = session['email']
                    user = users_collection.find_one({'email': email})
                    if user:
                        name = user.get('name')
                
                # Insert document into light_toggle collection
                light_toggle_collection.insert_one({
                    'rack_number': relay_num,
                    'action': 'turn_on',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'),
                    'controlled_by': name if name else 'Unknown'  # Use user's name or 'Unknown' if not found
                })
                
                return f"Relay {relay_num} turned on successfully"
            else:
                return f"Failed to turn on relay {relay_num}. Status code: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return f"Invalid relay number: {relay_num}"

@app.route('/turn_off/<int:relay_num>')
def turn_off(relay_num):
    if 1 <= relay_num <= num_relays:
        try:
            # Choose the appropriate ESP32 IP address based on relay number
            esp32_ip_address = ESP32_IP_ADDRESS if relay_num <= 2 else ESP32_IP_ADDRESS2
            response = requests.get(f'{esp32_ip_address}/turn_off/{relay_num}')
            
            if response.status_code == 200:
                # Update the relay state in MongoDB
                light_state_collection.update_one(
                    {'relay_num': relay_num},
                    {'$set': {'state': False}},
                    upsert=True  # Create a new document if it doesn't exist
                )
                
                name = None
                if 'email' in session:
                    email = session['email']
                    user = users_collection.find_one({'email': email})
                    if user:
                        name = user.get('name')
                
                # Insert document into light_toggle collection
                light_toggle_collection.insert_one({
                    'rack_number': relay_num,
                    'action': 'turn_off',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %I:%M:%S %p'),
                    'controlled_by': name if name else 'Unknown'  # Use user's name or 'Unknown' if not found
                })
                
                return f"Relay {relay_num} turned off successfully"
            else:
                return f"Failed to turn off relay {relay_num}. Status code: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return f"Invalid relay number: {relay_num}"
    
# Add this route to your Flask app
@app.route('/get_relay_states', methods=['GET'])
def get_relay_states():
    relay_states = {}  # Initialize an empty dictionary to store relay states

    # Retrieve relay states from MongoDB collection
    light_states = mongodb_db.light_state.find({}, {'_id': 0, 'relay_num': 1, 'state': 1})

    for state in light_states:
        relay_states[state['relay_num']] = state['state']

    return jsonify(relay_states)


@app.route('/insert_schedule_data', methods=['POST'])
def insert_schedule_data():
    try:
        data = request.get_json()
        rack = data.get('rack')
        month_year_selected_str = data.get('monthYearSelected')  # Assuming it's in the format '%d %B %Y'
        time_start = data.get('time_start')
        time_end = data.get('time_end')
        temperature = data.get('temperature')
        grow_light_status = data.get('grow_light_status')

        # Convert the string date to a datetime object
        month_year_selected_date = datetime.strptime(month_year_selected_str, '%d %B %Y')

        # Extract the month, day, and year
        month = month_year_selected_date.month
        day = month_year_selected_date.day
        year = month_year_selected_date.year

        # Format the date as a string in the desired format
        month_year_selected_formatted = month_year_selected_date.strftime('%d %B %Y')

        # Check if start and end times are the same, if so, don't insert
        if time_start != time_end:
            # Store data in MongoDB alerts collection
            schedule_collection.insert_one({
                'rack': rack,
                'month': month,  # Numeric month
                'day': day,      # Numeric day
                'year': year,    # Numeric year
                'monthYearSelected': month_year_selected_formatted,
                'time_start': time_start,
                'time_end': time_end,
                'temperature': temperature,
                'grow_light_status': grow_light_status
            })

            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Start and end times are the same. Record not inserted.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def relay_control_logic():
    temperature_sent = False  # Flag to track if temperature control message has been sent
    while True:
        # Fetch schedule data from MongoDB
        schedule_data = mongodb_db.schedule.find().sort([("year", 1), ("month", 1), ("day", 1), ("time_start", 1)])

        # Iterate over each schedule entry
        for entry in schedule_data:
            rack_number = entry['rack']  # Convert rack_number to an integer
            time_start = entry['time_start']
            time_end = entry['time_end']
            grow_light_status = entry['grow_light_status']
            temperature = entry['temperature']
            year = int(entry['year'])  # Convert year to an integer
            month = int(entry['month'])  # Convert month to an integer
            day = int(entry['day'])  # Convert day to an integer

            # Get the current time in Asia/Manila timezone
            current_time_manila = datetime.now(pytz.timezone('Asia/Manila'))
            formatted_time = current_time_manila.strftime('%H:%M')

            # Check if the current date is within the schedule date range
            if (current_time_manila.year, current_time_manila.month, current_time_manila.day) == (year, month, day):
                # Check if the current time is within the schedule time range
                if time_start <= formatted_time <= time_end:
                    # Determine the appropriate relay action based on grow_light_status
                    relay_action = 'turn_on' if grow_light_status.lower() == 'on' else 'turn_off'
                    topic = f'garlicgreenhouse/rack{rack_number}state'
                    # Modify the message payload based on relay_action
                    message = "1.0" if relay_action == 'turn_on' else "0.0"
                    try:
                        mqtt_publish.single(topic, payload=message, hostname=mqtt_broker)
                        print(f"Relay control successful: {relay_action} Rack {rack_number}")
                    except Exception as e:
                        print(f"Error controlling relay: {str(e)}")

                    # Set temperature_sent flag to True when the appropriate time comes
                    temperature_sent = True

                # Check if the current time is approaching time_end
                elif formatted_time >= time_end:
                    # Determine the opposite relay action based on grow_light_status
                    opposite_relay_action = 'turn_off' if grow_light_status.lower() == 'on' else 'turn_on'
                    topic = f'garlicgreenhouse/rack{rack_number}state'
                    # Modify the message payload based on opposite_relay_action
                    message = "1.0" if opposite_relay_action == 'turn_on' else "0.0"
                    try:
                        mqtt_publish.single(topic, payload=message, hostname=mqtt_broker)
                        print(f"Opposite Relay control successful: {opposite_relay_action} Rack {rack_number}")
                    except Exception as e:
                        print(f"Error controlling opposite relay: {str(e)}")

                    # Delete the processed entry from MongoDB
                    result = mongodb_db.schedule.delete_one({'rack': rack_number, 'time_end': time_end})
                    if result.deleted_count == 1:
                        print("Schedule entry deleted successfully.")
                    else:
                        print("Failed to delete schedule entry.")

        # Check if temperature control message has been sent and send it only once
        if temperature_sent:
            try:
                # Send the temperature control message
                temperature_topic = "garlicgreenhouse/ac_state"
                temperature_message = float(temperature)  # Convert temperature to float
                mqtt_publish.single(temperature_topic, payload=temperature_message, hostname=mqtt_broker)
                print(f"Temperature control successful: Temperature set to {temperature}")
            except Exception as e:
                print(f"Error controlling temperature: {str(e)}")
            finally:
                # Reset the flag
                temperature_sent = False

        # Sleep for a specific interval before checking the schedule again
        time.sleep(60)  # Adjust the interval as needed

# Start the thread for relay control logic
relay_control_thread = threading.Thread(target=relay_control_logic)
relay_control_thread.daemon = True
relay_control_thread.start()

@app.route('/delete_schedule/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    try:
        # Assuming you are using MongoDB ObjectId for schedule IDs
        schedule_id = ObjectId(schedule_id)
        result = schedule_collection.delete_one({'_id': schedule_id})

        if result.deleted_count > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Schedule not found.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
        
@app.route("/increase")
def increase_temperature():
    requests.get(f"{esp32_url}/up")
    return "OK"

@app.route("/decrease")
def decrease_temperature():
    requests.get(f"{esp32_url}/down")
    return "OK"

@app.route("/power")
def toggle_power():
    requests.get(f"{esp32_url}/power")
    return "OK"

@app.route('/set', methods=['GET'])
def set_temperature():
    temp_param = request.args.get('temp')
    new_temperature = float(temp_param)
    update_temperature(new_temperature)
    return 'OK'

def update_temperature(new_temperature):
    global current_temperature

    # Get the current date and time
    current_datetime = datetime.now()

    # Format date and time strings
    formatted_date = current_datetime.strftime('%Y-%m-%d')
    formatted_time = current_datetime.strftime('%I:%M:%S %p')

    # Convert new_temperature to Int32
    new_temperature_int32 = Int64(new_temperature)

    # Save the new temperature in the MongoDB collection
    controlled_by = 'Unknown'
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({'email': email})
        if user:
            controlled_by = user.get('name')

    # Include controlled_by in temperature_data
    temperature_data = {
        "temperature": new_temperature_int32,
        "date": formatted_date,
        "time": formatted_time,
        "controlled_by": controlled_by
    }

    # Insert the data into the 'ac_control' collection
    mongodb_db.ac_control.insert_one(temperature_data)

    # Query the latest temperature data from the MongoDB collection
    latest_temperature_data = mongodb_db.ac_control.find_one(
        {},
        {"temperature": 1},
        sort=[("date", -1), ("time", -1)]
    )

    # Set current_temperature with the latest value from the collection
    if latest_temperature_data:
        previous_temperature = current_temperature
        current_temperature = latest_temperature_data["temperature"]

        # Update the 'status' field in the 'aircon_tmp' collection
        aircon_tmp_data = {
            "c_temp": current_temperature,
            "status": current_temperature == new_temperature_int32
        }

        # Convert previous_temperature to Int32
        previous_temperature_int32 = Int64(previous_temperature)

        # Insert or update the data in the 'aircon_tmp' collection
        mongodb_db.aircon_tmp.update_one(
            {"c_temp": previous_temperature_int32},
            {"$set": {"status": False}},
        )

        mongodb_db.aircon_tmp.update_one(
            {"c_temp": current_temperature},
            {"$set": aircon_tmp_data},
            upsert=True
        )

    # Send HTTP request to ESP32 to update temperature
    requests.get(f'http://{ac_ip}/set?temp={current_temperature}')


def setup_current_temperature():
    global current_temperature

    # Query the latest temperature data from the MongoDB collection
    latest_temperature_data = mongodb_db.ac_control.find_one(
        {},
        {"temperature": 1},
        sort=[("timestamp", -1)]
    )

    # Set current_temperature with the latest value from the collection
    if latest_temperature_data:
        current_temperature = latest_temperature_data["temperature"]
    else:
        # Set a default value if no temperature data is found
        current_temperature = 17

# Call the setup function at the beginning of your script
setup_current_temperature()

class Camera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.lock = threading.Lock()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        with self.lock:
            success, image = self.video.read()
            if not success:
                return None
            _, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()

def generate_frames(camera):
    while True:
        frame = camera.get_frame()
        if frame is None:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/feed')
def feed():
    return render_template('feed.html')

@app.route('/video_feed')
def video_feed():
     return Response(generate_frames(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/latest_controlled_by')
def latest_controlled_by():
    # Fetch the latest entries from the light_toggle collection
    latest_entries = light_toggle_collection.find({}, {'_id': 0, 'rack_number': 1, 'controlled_by': 1})

    # Initialize a dictionary to store controlled_by information for each rack
    controlled_by_dict = {}

    # Iterate over the latest entries and populate the controlled_by_dict
    for entry in latest_entries:
        rack_number = entry.get('rack_number')
        controlled_by = entry.get('controlled_by', 'Unknown')
        controlled_by_dict[rack_number] = controlled_by

    # Return the controlled_by information as JSON
    return jsonify(controlled_by_dict)


@app.route('/latest_ac_control')
def latest_ac_control():
    # Fetch the latest entry from the ac_control collection based on time and date
    latest_entry = ac_control_collection.find_one(sort=[('date', -1), ('time', -1)])

    # Extract the 'controlled_by' field from the latest entry
    controlled_by = latest_entry.get('controlled_by', 'Unknown')

    # Return the controlled_by information as JSON
    return jsonify({'controlled_by': controlled_by})

@app.route('/index')
def index():
    # Fetch user data
    user = mongodb_db.users.find_one({"email": session.get('email')})
    
    # Fetch schedule data from MongoDB and sort it
    schedule_data = mongodb_db.schedule.find().sort([("monthYearSelected", 1), ("time_start", 1)])
    
    # Convert MongoDB cursor to a list of dictionaries
    schedule_list = [entry for entry in schedule_data]
    
    
    return render_template('index.html', 
                           sensor_data=sensor_data, 
                           num_relays=num_relays,
                           schedule_list=schedule_list, 
                           current_temperature=current_temperature)
if __name__ == '__main__':
    # Connect MQTT client and subscribe to topics
    client.on_message = on_message
    client.connect(mqtt_broker, 1883)
    client.subscribe([
        (temperature_topic, 0),
        (humidity_topic, 0),
        (mqttLumens1Topic, 0),
        (mqttLumens2Topic, 0),
        (mqttLumens3Topic, 0),
        (mqttLumens4Topic, 0),
        (current_temperature_topic, 0),
        (LED_CONTROL_TOPIC1, 0),  # Subscribe to LED control topics
        (LED_CONTROL_TOPIC2, 0),
        (LED_CONTROL_TOPIC3, 0),
        (LED_CONTROL_TOPIC4, 0),
        (AC_CONTROL_TOPIC, 0),
    ])
    client.loop_start()

    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=8080)

