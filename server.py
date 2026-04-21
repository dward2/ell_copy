from flask import Flask, request, jsonify
import mongo
import base64
from pymongo import MongoClient
from mongo import collection, create_patient, update_patient_name
from mongo import create_patient_cpap, update_cpap_data
from datetime import datetime

app = Flask(__name__)


@app.route("/", methods=['GET'])
def server_status():
    return "server is running"


# validate mrn
def validate_server_mrn(mrn):
    '''Validates MRN from server
    request.
    Args:
        mrn: medical record number
    Returns:
        True if valid, error message if
        invalid.
    '''
    if not isinstance(mrn, int):
        return "MRN must be an integer"
    return True


# validate rn
def validate_server_rn(rn):
    '''Validates RN from server
    request.
    Args:
        rn: room number
    Returns:
        True if valid, error message if
        invalid.
    '''
    if not isinstance(rn, str):
        return "Room number must be a string"
    if not rn.isdigit():
        return "Room number must contain only digits"
    return True


# validate name
def validate_server_name(name):
    '''Validates patient name from
    server request. Makes sure it
    is a string. Allows dashes but
    no other special characters.
    Allows empty string.
    Args:
        name: the name value to validate.
    Returns:
        True if valid, or an error message string.
    '''
    if not isinstance(name, str):
        return "Name must be a string"
    for c in name.strip():
        if c.isalpha():
            continue
        elif c == " ":
            continue
        elif c == "-":
            continue
        else:
            return "Name contains invalid characters"
    return True


# validate pressure
def validate_server_pressure(pres):
    '''Validates CPAP pressure from server request.
    Checks that the pressure is an integer, and
    is between 4 and 25.
    Args:
        pres: the pressure value to validate.
    Returns:
        True if valid, or an error message string.

    '''
    if not isinstance(pres, int):
        return "CPAP pressure must be an integer"
    if pres < 4 or pres > 25:
        return "CPAP pressure must be between 4 and 25"
    return True


# validate cpap data
def validate_server_cpap_data(br, apnea):
    '''Validates breathing rate and
    apnea count from server request.
    Checks that apnea and breathing rate
    are integers and non-negative.
    Args:
        br: the breathing rate
        apnea: the apnea count
    Returns:
     True if valid, or an error message string.
    '''
    if not isinstance(br, int):
        return "Breathing rate must be an integer"
    if not isinstance(apnea, int):
        return "Apnea count must be an integer"
    if br < 0:
        return "Breathing rate cannot be negative"
    if apnea < 0:
        return "Apnea count cannot be negative"
    return True


def upload_processing(data):
    '''Processes and stores patient data in
    database.
    Args:
    data (dict): patient data containing mrn, room_number,
        and optionally name and CPAP data.
    Returns:
        tuple: (message dict, status_code)
    '''
    mrn = data["mrn"]
    room_number = data["room_number"]
    name = data.get("name", None)
    time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    patient = collection.find_one({"mrn": mrn})

    if patient is None:
        if "cpap_pressure" in data:
            create_patient_cpap(
                mrn, room_number,
                data["cpap_pressure"],
                data["apnea_count"],
                data["breathing_rate"],
                "",
                time,
                name=name
            )
        else:
            create_patient(mrn, room_number, name)
    else:
        if name is not None:
            update_patient_name(mrn, name)
        if "cpap_pressure" in data:
            update_cpap_data(
                mrn,
                data["cpap_pressure"],
                data["apnea_count"],
                data["breathing_rate"],
                "",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

    return {"message": "Success"}, 200


@app.route("/api/patient", methods=["POST"])
def upload_patient():
    data = request.get_json()
    message, status = upload_processing(data)
    return jsonify(message), status


@app.route("/rooms", methods=['GET'])
def get_rooms():
    return jsonify([100, 200, 300])


@app.route("/patient/<room>", methods=["GET"])
def get_patient_data_from_room(room):
    # implement to get:
    # name, mrn, apnea, breathing rate
    # latest cpap image
    # latest pressure
    # list of cpap timestamps
    print(room)
    patient = {"name": f"ella {room}", "mrn": 1234, "cpap image": "image_str",
               "times": ["mm/dd/yy 00:00", "01/30/04 00:00"], "pressure": 5,
               "apnea": 3, "br": 4}
    return jsonify(patient)


def decode_image(b64_string, filename):
    image_bytes = base64.b64decode(b64_string)
    with open(filename, "wb") as out_file:
        out_file.write(image_bytes)
    return None


@app.route("/cpap", methods=["GET"])
def get_cpap_from_time():
    # implement to get the cpap image string at specific time
    room = request.args.get("room")
    time = request.args.get("time")
    if time == "mm/dd/yy 00:00":
        with open("cpap1.png", "rb") as image_file:
            image_str = encode_image(image_file)  # get from mongo here
    if time == "01/30/04 00:00":
        with open("cpap2.png", "rb") as image_file:
            image_str = encode_image(image_file)  # get from mongo here
    filename = "cpap" + '_' + room + '_' + time.replace('/', '.')
    decode_image(image_str, filename)
    return filename, 200


@app.route("/pressure/<p>", methods=["POST"])
def new_pressure(p):
    try:
        p = int(p)
    except TypeError:
        return "invalid", 400

    if p >= 4 and p <= 25:
        print(f'add pressure {p}')
        return "added pressure", 200
    else:
        return "invalid", 400


def encode_image(image_file):
    image_bytes = image_file.read()
    img_str = base64.b64encode(image_bytes).decode("utf-8")
    return img_str


@app.route("/upload_image", methods=['POST'])
def upload_image():
    file = request.files["file"]

    # encode image to str
    image_str = encode_image(file)

    # upload image here with mongo file

    return "data received", 200


if __name__ == "__main__":
    app.run()
