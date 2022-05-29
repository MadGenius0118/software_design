import requests
import ast
import base64


server_name = "http://vcm-23051.vm.duke.edu:5011/"
# Local
# server_name = "http://127.0.0.1:5000/"


def add_patient_to_server(name_input,
                          id_input,
                          medical_image,
                          ecg_image,
                          ave_hr):
    """ Makes request to server to add specified patient information

    This function takes patient information as parameter inputs and makes
    a post request to the main server to store this patient
    information on the server.  It prints the server response to the
    console as well as returns it to the caller.

    Args:
        name_input (str): indicates the patient's name
        id_input (int): indicates the patient's medical record number / ID
        medical_image: image file encoded into base64 string
        ecg_image (b64-str): image file encoded into base64 string
        ave_hr (int): represents the patient's heart rate

    Returns:
        str: server response string
    """
    patient1 = {"name": name_input, "medical_record_number": id_input,
                "medical_image": medical_image, "ecg_image": ecg_image,
                "hr": ave_hr}
    r = requests.post(server_name + "api/new_patient", json=patient1)
    print(r.status_code)
    print(r.text)
    return r.text


# get a list of medical record number from database
def get_patient_id_list():
    """Gets the list of patient IDs from server database

    This function makes a GET request to the server called api/get_patient,
    and gets the returned dictionary called id_dict which has one key "ID"
    containing all the patient id numbers in database. Then, it gets the value
    stored in key "ID" of id_dict and returns back the list of medical record
    numbers stored in the database.

    Returns:
        patient_id (list): a list of currently stored patient id numbers in
                           the database on the server

    """
    r = requests.get(server_name + "api/get_patient")
    id_dict = ast.literal_eval(r.text)
    patient_id = id_dict["ID"]
    return patient_id


# get specific patient instance
def get_patient_from_server(id):
    """Gets the patient dictionary from server given the patient ID

    This function makes a variable GET request to the server called
    api/get_patient/<id_number> and gets the returned patient dictionary
    corresponding to the given id input. Then, the specific dictionary
    is returned, and it has the following format:

                    {"name": str,
                    "id": int,
                    "ecg_image": b64-encoded str,
                    "heart_rate": int,
                    "timestamp": str,
                    "medical_image": b64-encoded str}

    Args:
        id (str): indicates the patient's medical record number

    Returns:
        patient_dict (dict): a dictionary containing information of the
                             specified patient in the above format

    """
    r = requests. get(server_name + f"api/get_patient/{id}")
    patient_dict = ast.literal_eval(r.text)
    return patient_dict


# get specific patient's latest ecg image, hr and timestamp
def get_patient_latest(patient_dict):
    """Gets the latest patient ECG information given a specific patient
    dictionary

    This function takes a patient dictionary and gets the value of key "name",
    the value of key "id", the last value of key "ecg_image", the last value
    of key "heart_rate" and the last value of key "timestamp", and returns
    these elements separately.

    Args:
        patient_dict (dict): a dictionary containing information of the
                             specified patient

    Returns:
        name (str), id (int), latest_ecg_image (b64-encoded str), latest_hr
        (int), latest_timestamp (str): the patient name, id, encoded latest
                                       ECG image, latest heart rate, timestamp
                                       of the latest heart rate input

    """
    name = patient_dict["name"]
    id = patient_dict["id"]
    latest_ecg_image = patient_dict["ecg_image"][-1]
    latest_hr = patient_dict["heart_rate"][-1]
    latest_timestamp = patient_dict["timestamp"][-1]
    return name, id, latest_ecg_image, latest_hr, latest_timestamp


# convert b64 string into image file
def b64_string_to_file(b64_string, filename):
    """Decodes image from its b64-encoded string and saves it as the given
    filename

    This function takes in a b64-encoded string and decodes it into image
    bytes using base64.b64decode method. Then, it opens a file for writing
    with the given filename and saves the decoded image.

    Args:
        b64_string (b64-encoded str): the Base64 encoded image
        filename (str): the specified filename for the image to be saved

    Returns:
        None

    """
    image_bytes = base64.b64decode(b64_string)
    with open(filename, "wb") as out_file:
        out_file.write(image_bytes)
    return None


def main():
    # Successfully add patient
    add_patient_to_server("Ann Ables", 1, "", "", "")
    add_patient_to_server("Tony Stark", 2, "", "", "")
    add_patient_to_server("Kevin Pepper", 3, "", "", "")

    # fail to add patients
    add_patient_to_server("", "8jfh", "", "", "")
    add_patient_to_server("Bob", "", "", "", "")

    # retrieve a lists of patient id stored in database
    id_list = get_patient_id_list()
    print(id_list)


if __name__ == '__main__':
    main()
