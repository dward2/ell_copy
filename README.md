# Sleep Lab Monitoring

## Authors: Nika Ilieva, Ella Fortenbery

This project is a distributed client-server application for clinical sleep lab monitoring. The system consists of a patient-side GUI, a monitoring station GUI and a cloud deployed server backed by a MongoDB database.

The patient side GUI allows entry of patient information, analyzes uploaded CPAP data files for breathing rate and apnea events, displays a flow vs. time plot and uploads results to the server. It regularly (every 30 seconds) polls the server for updated pressure commands from the monitoring station.

The monitoring GUI displays patient data to lab technicians for any active room, allows side by side comparison of CPAP data history, gets flow vs. time data from the server and allows image saving locally. Allows new pressure commands to specific rooms.

The server is a Flask-based RESTful API deployed to a cloud virtual machine, backed by a MongoDB database. It handles patient data uploads, stores timestamped CPAP measurements and flow images, and serves data to both clients.


## How To Run
1. Make sure Python3 is installed.
2. Make sure that the libraries from requirements.txt are imported

## Patient-Side User Manual
1. Make sure server is running.
2. Open terminal and run patient_gui.py

![alt text](pictures/pgui_1.png)

*Entering Patient Information*

1. You will have the ability to input name, medical record number, room number and CPAP pressure.

2. Enter at least medical record number and room number.

![alt text](pictures/pgui_2.png)
![alt text](pictures/pgui_3.png)

3. Optionally, enter patient name and CPAP pressure.

![alt text](pictures/pgui_4.png)

*CPAP Data Analysis*

4. Click **Select CPAP File** to open a file browser and select a .txt CPAP file of interest. The GUI will calculate and display the breathing rate and apnea event count. If the apnea events are abnormal, the number will display in **red**. A flow vs. time plot image will display in the GUI.

![alt text](pictures/pgui_5.png)
![alt text](pictures/pgui_6.png)

*Uploading to Database*

After filling out required fields and optionally entering CPAP data the user has the option to upload the information to the server.

5.  Click **Upload** to send data to the server. The CPAP flow vs. time image will be appended with a timestamp/

![alt text](pictures/pgui_7.png)

*Updating Patient Data*

After first upload, the user can update patient name and CPAP pressure without changing the medical record number and room number.

8. Edit the patient name and upload. The server will replace the existing name.

![alt text](pictures/pgui_8.png)

9. Edit the CPAP pressure value. The pressure will be replaced in the server.

![alt text](pictures/pgui_9.png)

10. Choose a different CPAP data file. The apnea and breathing rate will be replaced. The flow vs. time image will be appended with a timestamp upon upload.
![alt text](pictures/pgui_10.png)
![alt text](pictures/pgui_11.png)
![alt text](pictures/pgui_12.png)

*Automatic Pressure Updates*

11. The client polls the server every 30 seconds. If monitoring station has commanded a new CPAP pressure for client's specific room, the pressure field and data in server update automatically.

![alt text](pictures/pgui_14.png)
![alt text](pictures/pgui_15.png)

*Resetting the Device*

12. Click **Reset** to clear all data in the GUI. The GUI is then ready to be used for a new patient.

![alt text](pictures/pgui_13.png)

*Status Bar*

13. Refer to the status bar for feedback, missing required fields and instructions.


## Monitoring Side User Manual

1. Run the monitering_gui.py file.

*Patient Information*
![alt text](pictures/qgui_1.png)

2. Select a room from the **room dropdown**. The patient panel will populate wiht patient information (name, medical record number, latest CPAP pressure, apnea events and breathing rate). If the apnea events are 2 or higher, it is displayed in red as a clinical alert.

![alt text](pictures/qgui_2.png)

![alt text](pictures/qgui_3.png)

3. The most recent CPAP image appears on the right. To view historical readings, select a timestamp from the **time dropdown**.The past CPAP image will appear on the left.
![alt text](pictures/qgui_4.png)

4. To save past or recent image, click **Save image** button below the display. A file dialog will open to choose the save location and file name.

![alt text](pictures/qgui_5.png)

*Sending a Pressure Command*

5. Make sure correct room is selected.

6. Enter a new pressure value in the new pressure field.

![alt text](pictures/pgui_14.png)

7. Click **Submit**. On success, the field will clear.

![alt text](pictures/pgui_15.png)

*Switching Rooms*

8. Upon selecting a different room from the dropdown the all data will automatically update.

*Automatic-updating*

10. The interface polls the server every 10 seconds. Room lists and patient data for the currently selected room update automatically. If new CPAP data has been uploaded by the patient-side GUI, it will display without any action needed from the monitoring side.


## API Reference Guide
Server URL: 'http://127.0.0.1:5000'

#### GET /
Check that server is running.

**Response:** 200 OK — plain text "server is running"

#### POST /api/patient
Create or update a patient record. If the MRN already exists, name, pressure, and CPAP data are updated selectively. When cpap_pressure is provided, breathing_rate and apnea_count are also required.

**Request body (JSON):**

| Field | Type | Required | Notes |
|---|---|---|---|
| mrn | integer | required | Medical record number |
| room_number | string | required | Digits only, e.g. "12" |
| name | string | optional | Letters, spaces, and hyphens only |
| cpap_pressure | integer | optional | 4–25 cmH₂O |
| breathing_rate | integer | conditional | Required with cpap file selected; non-negative |
| apnea_count | integer | conditional | Required with cpap file selected; non-negative |
| image | string | optional | Base64-encoded CPAP image |

**Responses:**
- 200 — {"message": "Success"}
- 400 — {"error": "<validation message>"}

#### GET /rooms
List all active room numbers.

**Response:** 200 — JSON array of room number strings, e.g. ["101", "102"]

### GET /patient/{room}
Get patient data for a given room. CPAP timestamps are returned sorted chronologically.

**Path parameter:** room — room number string

**Response:**
- 200:
{
  "name": "Nika Ilieva",
  "mrn": 123,
  "pressure": 10,
  "br": 14,
  "apnea": 3,
  "times": ["04/22/26 08:30:00", "04/22/26 09:15:00"]
}
- 400 — "no patient in room"

#### GET /cpap
Retrieve and decode a CPAP image for a specific room and timestamp. Saves the image as a file on the server and returns the filename.

**Query parameters:**

| Param | Type | Required | Notes |
|---|---|---|---|
| room | string | required | Room number |
| time | string | required | Format: MM/DD/YY HH:MM:SS |

**Responses:**
- 200 — filename string, e.g. "cpap_101_04.22.26 08:30:00"
- 400 — "no timestamp"

#### POST /pressure
Update the commanded CPAP pressure for a room.

**Request body (JSON):**

| Field | Type | Required | Notes |
|---|---|---|---|
| room | string | required | Digits only |
| pressure | integer | required | 4–25 cmH₂O |

**Responses:**
- 200 — "pressure added"
- 400 — "<validation message>"

#### GET /pressure
Get the current commanded CPAP pressure for a room. Intended for the patient-side client to poll for pressure updates.

**Query parameters:**

| Param | Type | Required |
|---|---|---|
| room | string | required |

**Responses:**
- 200 — {"pressure": 12}
- 400 — "room is required"
- 404 — "room not found" or "no pressure commanded"

Acknowledgement: Used AI to creare API guide https://claude.ai/share/85318bb6-ed11-4db1-80ba-2fb280382396

## Video Demo

Access Link: https://youtu.be/JTl_IXCTha0

## Licensing

MIT License

Copyright (c) 2026 Nika Ilieva, Ella Fortenbery

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

