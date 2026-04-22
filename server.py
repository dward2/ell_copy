from flask import Flask, request, jsonify
import mongo
import base64
from pymongo import MongoClient
from mongo import collection, create_patient, update_patient_name
from mongo import create_patient_cpap, update_cpap_data
from mongo import get_room_list, get_patient, reset_db, change_pressure
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


def validate_uploaded_data(data):
    '''Validates incoming patient upload data.
    Checks for required fields and validates
    data types and values.
    Args:
        data (dict): the uploaded patient data.

    Returns:
        True if valid, or an error message string if invalid.
    '''
    if not isinstance(data, dict):
        return "Invalid data format"
    if "mrn" not in data:
        return "MRN is required"
    if "room_number" not in data:
        return "Room number is required"

    mrn_check = validate_server_mrn(data["mrn"])
    if mrn_check is not True:
        return mrn_check

    rn_check = validate_server_rn(data["room_number"])
    if rn_check is not True:
        return rn_check

    if "name" in data:
        name_check = validate_server_name(data["name"])
        if name_check is not True:
            return name_check

    if "cpap_pressure" in data:
        pres_check = validate_server_pressure(data["cpap_pressure"])
        if pres_check is not True:
            return pres_check
        if "breathing_rate" not in data:
            return "Breathing rate required with CPAP pressure"
        if "apnea_count" not in data:
            return "Apnea count required with CPAP pressure"
        cpap_check = validate_server_cpap_data(
            data["breathing_rate"], data["apnea_count"]
        )
        if cpap_check is not True:
            return cpap_check

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
    time = datetime.now()
    image_str = data.get("image")
    patient = collection.find_one({"mrn": mrn})
    pressure = data.get("cpap_pressure")
    if patient is None:
        if "cpap_pressure" in data:
            create_patient_cpap(
                mrn,
                room_number,
                pressure,
                data["apnea_count"],
                data["breathing_rate"],
                image_str,
                time,
                name=name
            )
        else:
            create_patient(mrn, room_number, name)
    else:
        if name is not None:
            update_patient_name(mrn, name)
        if pressure is not None:
            change_pressure(room_number, pressure)
        if image_str in data:
            update_cpap_data(
                mrn,
                data["apnea_count"],
                data["breathing_rate"],
                data["image"],
                datetime.now()
            )

    return {"message": "Success"}, 200


@app.route("/api/patient", methods=["POST"])
def upload_patient():
    data = request.get_json()
    message, status = upload_processing(data)
    return jsonify(message), status


@app.route("/rooms", methods=['GET'])
def get_rooms():
    rooms = get_room_list()
    return jsonify(rooms), 200


def format_time(dt):
    return dt.strftime("%m/%d/%y %H:%M:%S")


@app.route("/patient/<room>", methods=["GET"])
def get_patient_data_from_room(room):
    patient = get_patient(room)
    if patient is None:
        return "no patient in room", 400
    # sort datetimes
    sorted_data = sorted(
        patient["cpap_data"],
        key=lambda x: x["time"]
    )
    display_patient = {"name": patient["name"],
                       "mrn": patient['mrn'],
                       "pressure": patient['pressure'],
                       "br": patient['breathing_rate'],
                       "apnea": patient['apnea_count'],
                       "times": [
                            format_time(entry["time"])
                            for entry in patient["cpap_data"]
                                ]
                       }
    return jsonify(display_patient), 200


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
    # retrieve from db
    patient = get_patient(room)
    for entry in patient["cpap_data"]:
        if entry["time"] == time:
            image_str = entry["image"]
            break
    else:
        return "no timestamp", 400
    # decode
    filename = "cpap" + '_' + room + '_' + time.replace('/', '.')
    decode_image(image_str, filename)
    return filename, 200


@app.route("/pressure", methods=["POST"])
def new_pressure():
    data = request.get_json()
    room = data.get("room")
    p = data.get("pressure")
    valid = validate_server_pressure(p)
    if valid is True:
        change_pressure(room, p)
        return "pressure added", 200
    else:
        return "invalid", 400


def encode_image(image_file):
    image_bytes = image_file.read()
    img_str = base64.b64encode(image_bytes).decode("utf-8")
    return img_str


if __name__ == "__main__":
    app.run()
