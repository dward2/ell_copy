from flask import Flask, request, jsonify
import mongo
import base64

app = Flask(__name__)


@app.route("/", methods=['GET'])
def server_status():
    return "server is running"


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
