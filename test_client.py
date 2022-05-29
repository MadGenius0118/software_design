# test with b64_string_to_file

def test_b64_string_to_file():
    from client import b64_string_to_file
    from patient_side_GUI import convert_image_file_to_b64_string
    import filecmp
    import os
    b64str = convert_image_file_to_b64_string("images/acl1.jpg")
    b64_string_to_file(b64str, "test_image_output.jpg")
    answer = filecmp.cmp("images/acl1.jpg",
                         "test_image_output.jpg")
    os.remove("test_image_output.jpg")
    expected = True
    assert answer == expected


def test_get_patient_latest():
    from client import get_patient_latest
    test_dict = {"name": "TS",
                 "id": 19,
                 "heart_rate": [100, 80, 90],
                 "ecg_image": ["/9j/4AAQSkZ",
                               "/9j/4AAQ8fa",
                               "/9j/4AAMADG"],
                 "timestamp": ["2021-11-24 01:23:03",
                               "2021-11-24 01:23:35",
                               "2021-11-24 01:28:10"]
                 }
    expected_name = "TS"
    expected_id = 19
    expected_hr = 90
    expected_ecg_image = "/9j/4AAMADG"
    expected_timestamp = "2021-11-24 01:28:10"
    name, id, latest_ecg_image, latest_hr, latest_timestamp = \
        get_patient_latest(test_dict)
    assert expected_name == name
    assert expected_id == id
    assert expected_hr == latest_hr
    assert expected_timestamp == latest_timestamp
    assert expected_ecg_image == latest_ecg_image
