# Test for MongoDB database
import pytest
from main_server import initialize_server

initialize_server()


# route api/new_patient
# validate_new_patient


@pytest.mark.parametrize("input_dict, expected", [
    ({"medical_record_number": ""}, ("Make sure to enter the "
                                     "patient id ", 400)),
    ({"medical_record_number": 1}, (True, 200)),
    ({"medical_record_number": "90"}, (True, 200))
])
def test_validate_new_patient(input_dict, expected):
    from main_server import validate_new_patient
    answer = validate_new_patient(input_dict)
    assert expected == answer


# convert_patient_id
@pytest.mark.parametrize("id_no, expected", [
    (12, (12, 200)),
    ("18", (18, 200)),
    ("v129", (False, 400))
])
def test_convert_patient_id(id_no, expected):
    from main_server import convert_patient_id
    answer = convert_patient_id(id_no)
    assert expected == answer


# find_patient_id
def test_find_patient_id():
    from main_server import find_patient_id
    from main_server import add_database_entry
    expected_id = 118
    expected_name = "TS"
    entry_to_delete = add_database_entry(expected_name,
                                         expected_id,
                                         "", "", "")
    answer = find_patient_id(expected_id)
    entry_to_delete.delete()
    assert answer.medical_record_number == expected_id
    assert answer.name == expected_name


def test_find_patient_id_missing():
    from main_server import find_patient_id
    expected_id = 612783
    answer = find_patient_id(expected_id)
    expected = False
    assert answer == expected


# add_database_entry
def test_add_database_entry():
    from main_server import add_database_entry
    expected_id = 18
    expected_name = "James Smith"
    answer = add_database_entry(expected_name,
                                expected_id,
                                "",
                                "",
                                "")
    answer.delete()
    assert answer.name == expected_name
    assert answer.medical_record_number == expected_id


# ecg_timestamp
def test_ecg_timestamp():
    from main_server import ecg_timestamp
    import re
    expected = re.compile("....-..-.. ..:..:..")
    answer = ecg_timestamp()
    assert bool(re.match(expected, answer))


# patient_list
def test_patient_list():
    from main_server import patient_list
    from main_server import add_database_entry
    import ssl
    from pymodm import connect
    connect("mongodb+srv://MG118:cfy118@bme547.jakg4.mongodb.net/test_db"
            "?retryWrites=true&w=majority", ssl_cert_reqs=ssl.CERT_NONE)
    add_database_entry("", 1, "", "", "")
    add_database_entry("", 2, "", "", "")
    add_database_entry("", 3, "", "", "")
    answer = patient_list()
    expected = {"ID": [1, 2, 3]}
    assert answer == expected
