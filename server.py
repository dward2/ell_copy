from flask import Flask, request, jsonify
import mongo
import base64
from pymongo import MongoClient
from mongo import create_patient, update_patient_name, append_cpap_data
from mongo import get_room_list, get_patient, change_pressure
from mongo import replace_patient_in_room
from datetime import datetime

app = Flask(__name__)


@app.route("/", methods=['GET'])
def server_status():
    """
    Check server health/status.

    Returns:
        str: Simple message indicating the server is running.
    """
    return "server is running"


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
    if 'image' in data:
        if "breathing_rate" not in data:
            return "Breathing rate required with CPAP file"
        if "apnea_count" not in data:
            return "Apnea count required with CPAP file"
        cpap_check = validate_server_cpap_data(
            data["breathing_rate"], data["apnea_count"]
        )
        if cpap_check is not True:
            return cpap_check
    return True


def upload_processing(data):
    mrn = data["mrn"]
    room = data["room_number"]
    name = data.get("name")
    pressure = data.get("cpap_pressure")
    image = data.get("image")
    br = data.get("breathing_rate")
    apnea = data.get("apnea_count")
    now = datetime.now()

    patient = get_patient(room)

    # --- CASE 1: empty room ---
    if patient is None:
        create_patient(mrn, room, name)

    # --- CASE 2: different patient in same room ---
    elif patient["mrn"] != mrn:
        replace_patient_in_room(mrn, room, name)

    # --- CASE 3: same patient ---
    else:
        if name is not None:
            update_patient_name(room, name)

    # --- independent updates ---
    if pressure is not None:
        change_pressure(room, pressure)

    if image is not None:
        append_cpap_data(room, apnea, br, image, now)

    return {"message": "Success"}, 200


@app.route("/api/patient", methods=["POST"])
def upload_patient():
    """
    API endpoint to upload patient data.

    Validates incoming JSON and stores it in the database.

    Returns:
        JSON response with status message and HTTP status code.
    """
    data = request.get_json()
    validate = validate_uploaded_data(data)
    if validate is not True:
        return jsonify({"error": validate}), 400
    message, status = upload_processing(data)
    return jsonify(message), status


@app.route("/rooms", methods=['GET'])
def get_rooms():
    """
    Retrieve list of active room numbers.

    Returns:
        JSON list of room numbers and HTTP 200 status.
    """
    rooms = get_room_list()
    return jsonify(rooms), 200


def format_time(dt):
    """
    Format datetime object into display string.

    Args:
        dt (datetime): Datetime object.

    Returns:
        str: Formatted time string (MM/DD/YY HH:MM:SS).
    """
    return dt.strftime("%m/%d/%y %H:%M:%S")


@app.route("/patient/<room>", methods=["GET"])
def get_patient_data_from_room(room):
    """
    Retrieve patient data for a given room.

    Includes patient info and sorted CPAP timestamps.

    Args:
        room (str): Room number.

    Returns:
        JSON containing patient data or error message.
    """
    patient = get_patient(room)
    if patient is None:
        return "no patient in room", 400

    cpap_data = patient.get("cpap_data")

    if cpap_data:
        sorted_data = sorted(
            cpap_data,
            key=lambda x: x.get("time")
        )
        times = [
            format_time(entry.get("time"))
            for entry in sorted_data
        ]
    else:
        times = None
    display_patient = {"name": patient.get("name"),
                       "mrn": patient.get("mrn"),
                       "pressure": patient.get("pressure"),
                       "br": patient.get("breathing_rate"),
                       "apnea": patient.get("apnea_count"),
                       "times": times
                       }
    return jsonify(display_patient), 200


def decode_image(b64_string, filename):
    """
    Decode a base64-encoded image and save to file.

    Args:
        b64_string (str): Base64 encoded image string.
        filename (str): Output file path.

    Returns:
        None
    """

    image_bytes = base64.b64decode(b64_string)
    with open(filename, "wb") as out_file:
        out_file.write(image_bytes)
    return None


@app.route("/cpap", methods=["GET"])
def get_cpap_from_time():
    """
    Retrieve a CPAP image for a specific room and timestamp.

    Query Params:
        room (str): Room number.
        time (str): Formatted timestamp.

    Returns:
        Filename of decoded image or error message.
    """
    room = request.args.get("room")
    time = request.args.get("time")
    # retrieve from db
    patient = get_patient(room)
    patient = get_patient(room)
    if patient is None:
        return "room not found", 404
    for entry in patient["cpap_data"]:
        if format_time(entry["time"]) == time:
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
    """
    Update CPAP pressure for a given room.

    Expects JSON payload with:
        - room (str)
        - pressure (int)

    Returns:
        Status message and HTTP status code.
    """
    data = request.get_json()
    room = data.get("room")
    p = data.get("pressure")
    if not room:
        return "room is required", 400
    rn_valid = validate_server_rn(room)
    if rn_valid is not True:
        return rn_valid, 400
    valid = validate_server_pressure(p)
    if valid is not True:
        return valid, 400
    change_pressure(room, p)
    return "pressure added", 200


@app.route("/pressure", methods=["GET"])
def get_pressure():
    '''Gets the current CPAP pressure for a specific
    room. Needed for patient-side client query to
    update pressure commanded by monitoring station.
    Args:
        room(str): room number
    Returns:
        JSON with pressure and 200, or an error
    '''
    room = request.args.get("room")
    if not room:
        return "room is required", 400
    patient = get_patient(room)
    if patient is None:
        return "room not found", 404
    pressure = patient.get("pressure")
    return jsonify({"pressure": pressure}), 200


def encode_image(image_file):
    """
    Encode an image file as a base64 string.

    Args:
        image_file: File-like object.

    Returns:
        str: Base64-encoded image string.
    """
    image_bytes = image_file.read()
    img_str = base64.b64encode(image_bytes).decode("utf-8")
    return img_str


if __name__ == "__main__":
    app.run()
