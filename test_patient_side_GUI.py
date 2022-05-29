import pytest
from PIL import ImageTk, Image
from tkinter import ttk
import tkinter as tk

# patient_side GUI
# convert_image_file_to_b64_string


def test_convert_image_file_to_b64_string():
    from patient_side_GUI import convert_image_file_to_b64_string
    x = convert_image_file_to_b64_string("images/acl1.jpg")
    expected = x[0:20]
    b64_str = convert_image_file_to_b64_string("images/acl1.jpg")
    assert b64_str[0:20] == expected


# load_and_resize_image
def test_image_resize():
    from patient_side_GUI import image_resize
    original_pic = Image.open("images/acl1.jpg")
    expected_width = round(original_pic.size[0] * 0.5)
    expected_height = round(original_pic.size[1] * 0.5)
    answer_width, answer_height = image_resize("images/acl1.jpg")
    assert expected_width == answer_width
    assert expected_height == answer_height
