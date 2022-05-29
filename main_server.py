import pymodm.errors
from flask import Flask, request
from pymodm import connect
from database_definition import Patient
from datetime import datetime

app = Flask(__name__)


def initialize_server():
    """Initializes server connection to database

    This function initializes the server connection to MongoDB database.
    The data will be stored into a MongoDB folder called patient_db.

    Args:
        None

    Returns:
        None

    """
    print("Connecting ....")
    import ssl
    connect("mongodb+srv://MG118:cfy118@bme547.jakg4.mongodb.net/patient_db"
            "?retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
    print("Connection attempt finish")


@app.route("/", methods=["GET"])
def status():
    """Used to indicate that the server is running
    """
    return "Server is on"


@app.route("/api/new_patient", methods=["POST"])
def new_patient():
    """Implements route /api/new_patient for new patient registration
     and medical / ECG images uploading

     The route /api/new_patient is a POST request that receives
     JSON-encoded string with the following format:
                    {"name": str,
                    "medical_record_number": int,
                    "medical_image": b64-string,
                    "ecg_image": b64-string,
                    "hr": int}

    The function calls the main_patient function to validate,
    find existed patient if any and to store information to
    MongoDB database.

    Returns:
        str, int: returns the appropriate message followed by status code 200
                  or error code 400.

    """
    in_data = request.get_json()
    resp, status_code = main_patient(in_data)
    return resp, status_code


def main_patient(in_data):
    """Main execution function for route:/api/new_patient for new patient
    registration and medical / ECG images uploading

        The function takes the input and first calls validate_new_patient
    function to check for if the input data contains the patient id number.
    If not, an error message with status code 400 will be returned. If the id
    is existed, it will then try to convert the input id into numeric value
    if possible.convert_patient_id function will return the converted
    patient id if the input id can be converted. Then it will calls
    find_patient_id function to obtain the patient's entry by searching
    through the MongoDB database for the given id. If a patient is not
    found, a new patient entry will be created containing with the unique
    patient id and other information. Otherwise, input information will
    be added to the existed patient's entry. Lastly, if no further new
    information (name, medical or ecg images) updated, a message saying
    " no further update for patient" will return followed by status code 200.

    Returns:
        str, int: returns the appropriate message followed by status code 200
                  or error code 400.

    """
    resp, status_code = validate_new_patient(in_data)
    if status_code == 400:
        return resp, status_code
    id = in_data["medical_record_number"]
    patient_id, status_code = convert_patient_id(id)
    if status_code == 400:
        return f"The input {id} cannot be converted " \
               f"into integer", status_code
    patient = find_patient_id(patient_id)
    if patient is False:
        add_database_entry(in_data["name"],
                           patient_id,
                           in_data["medical_image"],
                           in_data["ecg_image"],
                           in_data["hr"])
        return f"New patient ID {patient_id} is registered", 200
    if in_data["name"] == "":
        in_data_name = None
    else:
        in_data_name = in_data["name"]
    if (in_data["medical_image"] == "") and (in_data["ecg_image"] == "") \
            and ((patient.name == in_data_name) | (in_data_name is None)):
        return f"No further updates for Patient ID {patient_id}", 200
    if in_data["name"] != "":
        patient.name = in_data["name"]
    if in_data["medical_image"] != "":
        patient.medical_image.append(in_data["medical_image"])
    if in_data["ecg_image"] != "":
        patient.ecg_image.append(in_data["ecg_image"])
        patient.heart_rate.append(in_data["hr"])
        patient.timestamp.append(ecg_timestamp())
    patient.save()
    return f"Patient ID {patient_id}'s data has been updated", 200


def validate_new_patient(in_data):
    """Checks for the existence of the medical record number in
    the input JSON dictionary

    The function takes in the dictionary containing with the key
    "medical_record_number", and checks if the respective value
    is empty or not. If the value exists, return a boolean value
    True followed by a status code 200. Otherwise, the function will
    return an error message saying "make sure to enter the patient id"
    along with a status code 400

     Args:
         in_data (dict): JSON-encoded string dictionary containing with
                         the key "medical_record_number"

    Returns:
        str (or bool), int: returns string message followed by status code 400
                         if no value exists for the key
                         "medical_record_number". Else, return True followed by
                         status code 200.

    """
    if in_data["medical_record_number"] == "":
        return "Make sure to enter the patient id ", 400
    return True, 200


def convert_patient_id(id_no):
    """Converts the patient id into integer value

    The function will try to convert the input values into integers.
    It can only convert the numeric strings, e.g. "1", "17" but letter
    strings like "u83", "12d". The function will return the converted
    version followed by status code 200 if applicable. Otherwise, return
    False along with status code 400.

    Args:
        id_no (int or str): represents the patient id/medical record number

    Returns:
        bool (or int), int: returns False and a status code 400 if cannot
                            convert the input data to integers. Otherwise,
                            returns the converted integers followed by a status
                            code 200.

    """
    try:
        patient_id = int(id_no)
    except ValueError:
        return False, 400
    return patient_id, 200


def find_patient_id(id_no):
    """Finds out the if current data has the input patient
    id and return that specific entry.

    The function takes one input (int) and search through
    the MongoDB database to find out the matching input value.
    In the end, it will return patient's entire entry as dictionary
    or False if not matching record found.

    Args:
        patient_id (int): represents the patient unique identification number

    Returns:
        Patient or bool: if patient id matches, returns the patient's entry
                         in a dictionary format. Else, returns False.

    """
    try:
        patient = Patient.objects.raw({"_id": id_no}).first()
    except pymodm.errors.DoesNotExist:
        patient = False
    return patient


def add_database_entry(name, id, medical_image, ecg_image, hr):
    """Stores the patient's information into established MongoDB
    database

    The function takes in 5 inputs (str, int, b64-string, b64-string,
    int) and stores medical record number into MongoDB database
    (Patient). Then it will validate whether the following fields (name,
    medical_image, ecg_image, hr) are empty. If not, add name and
    append the images into the patient's entry. If input ecg_image is
    not empty, the current timestamp are generated and passed into
    the database as well.

    Args:
        name (str): indicates the patient's name
        id (int): indicates the patient's medical record number / ID
        medical_image: image file encoded into base64 string
        ecg_image (b64-str): image file encoded into base64 string
        hr (int): represents the patient's heart rate

    Returns:
        Patient: contains the data saved to database

    """
    patient_to_add = Patient(medical_record_number=id)
    if name != "":
        patient_to_add.name = name
    if medical_image != "":
        patient_to_add.medical_image.append(medical_image)
    if ecg_image != "":
        patient_to_add.ecg_image.append(ecg_image)
        patient_to_add.heart_rate.append(hr)
        patient_to_add.timestamp.append(ecg_timestamp())
    answer = patient_to_add.save()
    return answer


def ecg_timestamp():
    """Outputs the current time in a string format

    The function is intended to output current time in a string format
    e.g "2021-10-28 2:39:60"

    Args:
        None

    Returns:
        str: returns a current datetime in a string format

    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return current_time


@app.route("/api/get_patient", methods=["GET"])
def get_patient_list():
    """Implements route /api/get_patient to obtain the a list
    of medical record numbers stored in the database

    The function calls another function patient_list to return
    currently stored patient id numbers in a list placed in a dictionary,
    followed by a status code 200

    Returns:
        dict: returns a dictionary with key called "ID", containing
              a list of patients' ID numbers from database

    """
    id_dict = patient_list()
    return id_dict, 200


def patient_list():
    """Main execution function for route get_patient to acquire
    the list of patient id

    The function returns the stored medical record numbers in a
    list placed in a dictionary called "id_dict".

    Returns:
        dict: returns a dictionary with key called "ID", containing
              a list of patients' ID numbers from database

    """
    id_list = []
    for patient in Patient.objects.raw({}):
        id_list.append(patient.medical_record_number)
    id_dict = {"ID": id_list}
    return id_dict


@app.route("/api/get_patient/<id>", methods=["GET"])
def get_patient_id(id):
    """Route /api/get_patient/<id> receives a GET request to return
    a specific patient instance with the given id input

    The function receives an input id and calls another function
    to find out the specific patient entry corresponding to the input
    id if such id can be converted into integer or matches with the
    existed record in the database.

    Args:
        id (str): indicates the patient's medical record number

    Returns:
        dict (or str), int: returns a patient info containing in a dictionary,
                            followed by a status code 200. Otherwise, return a
                            error message followed by a status code 400.

    """
    answer, status_code = main_get_patient_id(id)
    return answer, status_code


def main_get_patient_id(id):
    """Main execution function for route /api/get_patient/<id> to return
    patient's instance if existed

    The functions takes in one input (str) can tries to convert to integer
    by calling function convert_patient_id which will return converted
    id if it can be converted (e.g. "8", "9", "1"). Otherwise, returns
    error message saying the id cannot be converted followed by status
    code 400. Then, it will search through the database to find out
    the specific patient's instance associated with the id. If id not
    existed, it will return error message saying id does not exist.
    Otherwise, a specific patient instance will be passed in to a
    dictionary containing with the following keys:
                    {"name": str,
                    "id": int,
                    "ecg_image": b64-encoded str,
                    "heart_rate": int,
                    "timestamp": str,
                    "medical_image": b64-encoded str}

    Args:
        id (str): indicates the patient's medical record number

    Returns:
        dict (or str), int: returns a patient info containing in a dictionary,
                            followed by a status code 200. Otherwise, return a
                            error message followed by a status code 400.

    """
    patient_id, status_code = convert_patient_id(id)
    if status_code == 400:
        return f"{id} cannot be converted into integer", status_code
    patient = find_patient_id(patient_id)
    if patient is False:
        return f"{patient_id} does not exist in the current database", 400
    if patient.name is None:
        patient_name = "Not Specified"
    else:
        patient_name = patient.name
    patient_dict = {"name": patient_name,
                    "id": patient.medical_record_number,
                    "ecg_image": patient.ecg_image,
                    "heart_rate": patient.heart_rate,
                    "timestamp": patient.timestamp,
                    "medical_image": patient.medical_image}
    return patient_dict, 200


if __name__ == '__main__':
    initialize_server()
    # app.run()
    app.run(host="0.0.0.0", port=5011, )
