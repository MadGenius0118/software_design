import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from tkinter import filedialog, messagebox
import base64
import os

from client import add_patient_to_server
from ecg_analysis import raw_ecg_plot
from ecg_analysis import heart_rate_normalization


filename_ecg = ""
filename_medical = ""
ave_hr = 0


def convert_image_file_to_b64_string(f):
    """Converts image file (e.g *.jpeg /jpg) into b44-encoded string

    The function takes in filename and convert the designated image
    file into the b64 format string which can be stored into external
    database.

    Args:
        f (str): represents filename of the image file, e.g. "images/acl1.jpg".

    Returns:
        str: b64-encoded string

    """
    if f == "":
        return ""
    with open(f, "rb") as image_file:
        b64_bytes = base64.b64encode(image_file.read())
    b64_string = str(b64_bytes, encoding='utf-8')
    return b64_string


def image_resize(pic):
    """Calculates the reduced image width and height

    The function takes in the image file and multiplies adjusted
    factor 0.5 by the input image's original size. It returns the
    new width and height.

    Args:
        pic (str): indicates the filename of the image, e.g. "images/acl1.jpg"

    Returns:
        float, float: returns the calculated width and height of the image

    """
    pil_image = Image.open(pic)
    original_size = pil_image.size
    adj_factor = 0.5
    new_width = round(original_size[0] * adj_factor)
    new_height = round(original_size[1] * adj_factor)
    return new_width, new_height


def load_and_resize_image(pic):
    """Rescales and displays the image on GUI

    The function takes in one input filename (str) and resize the
    image by reducing half of its length. Then displaying the
    rescaled image onto the image holder position.

    Args:
        pic (str): indicates the filename of the image, e.g. "images/acl1.jpg"

    Returns:
        class PIL.ImageTK.PhotoImage: returns a tk-compatible image variable
                                      under the class PhotoImage

    """
    pil_image = Image.open(pic)
    new_width, new_height = image_resize(pic)
    resized_image = pil_image.resize((new_width, new_height))
    tk_image = ImageTk.PhotoImage(resized_image)
    return tk_image


def create_output(name, id, medical_image, ecg_image, hr):
    """Interface between GUI and server

    The function is called by the GUI command function attached to
    the "OK" button of the GUI. It takes the data entered into
    the GUI and creates an output string that will be sent to
    the server by calling the "add_patient_to_server" function.
    It returns the response received from the server.

    Args:
        name (str): represents patient's name
        id (str): represents patient's medical record number / id
        medical_image (str): represents selected medical image in b64 string
        ecg_image (str): represents selected ecg image in b64 string
        hr (int): indicates the heart rate for selected ecg image

    Returns:
        str, str: returns a formatted string containing patient information
                  from the GUI, the response from server when adding the
                  patient

    """
    out_string = "Patient name: {}\n".format(name)
    out_string += "ID: {}\n".format(id)
    answer = add_patient_to_server(name, id, medical_image, ecg_image, hr)
    return out_string, answer


def design_window():
    """Creates the main GUI window for Patient database

    The function is intended to create a GUI window for uploading
    patient information to the external Patient database. It accepts
    information from the user entry box (name, ID) and combobox allowing
    users to select filetype. After select the image, it will automatically
    be displayed on the GUI. The raw ECG data file will be plotted and shown
    on the right side labeled as "ECG Image". The reset button is
    used to clear out all the input on the GUI. Upon hitting the Upload
    button and select "yes", the input information will be uploaded into
    cloud database, where appropriate message will be returned and displayed
    on GUI. The quit button shown on the top right corner allows users
    to safely quit the program.

    Returns:
        None

    """
    def ok_button_cmd():
        """Event to run when Upload button is pressed

        The function is connected to the "Upload" button of the GUI.
        Prior calling the function that sending requests to the server, GUI
        will pop up a small message window asking the final confirmation for
        uploading these patient's information. If selecting "yes", it will
        send POST request to the server. Then, the response will be displayed
        on GUI. The medical image and ecg image will be cleared out on the
        screen when user has confirmed to upload information.

        Returns:
            None

        """
        global filename_ecg
        global filename_medical
        global ave_hr
        name = name_data.get()
        id = id_data.get()
        answer = messagebox.askyesno("Confirmation",
                                     "Do you want to upload the files?")
        if answer:
            ecg_image = convert_image_file_to_b64_string(filename_ecg)
            medical_image = convert_image_file_to_b64_string(filename_medical)
            # Call external function to do the work
            out_string, answer = create_output(name,
                                               id,
                                               medical_image,
                                               ecg_image,
                                               ave_hr)
            output_string.configure(text=answer)
            if os.path.exists("ecg_test.jpeg"):
                os.remove("ecg_test.jpeg")
            messagebox.showinfo("status", f"{answer}")
            tk_image = load_and_resize_image("Resources/image_holder2.jpeg")
            my_img_ecg.image = tk_image
            my_img_ecg.configure(image=tk_image)
            my_img_medical.image = tk_image
            my_img_medical.configure(image=tk_image)
            filename_ecg = ""
            filename_medical = ""
            ave_hr = 0
        return

    def change_picture_cmd():
        """Changes the image being displayed on GUI

        The function allows user to select images from anywhere from
        local computer and displays them on GUI. Before selecting the image,
        user will need to select filetype from the dropdown list and choose the
        image or raw data. For demonstration, medical image initial
        directory is set as "images" folder and raw ecg data will be directed
        to "test_data" folder. For ecg raw data (*.csv), data will be plotted
        and displayed on screen, along with that text message regarding
        estimated heart rate will be shown on the right of the GUI.

        Returns:
            None

        """
        global filename_ecg
        global filename_medical
        global ave_hr
        if file_type.get() == "":
            messagebox.showinfo("Warning", "Please select a file type")
            return
        if file_type.get() == "Medical image (*.jpg / jpeg)":
            filename_medical = filedialog.askopenfilename(initialdir="images")
            if filename_medical == '':
                return
            tk_image = load_and_resize_image(filename_medical)
            my_img_medical.image = tk_image
            my_img_medical.configure(image=tk_image)
        else:
            raw_data = filedialog.askopenfilename(initialdir="test_data")
            if raw_data == "":
                return
            raw_ecg_plot(raw_data)
            filename_ecg = "ecg_test.jpeg"
            tk_image = load_and_resize_image(filename_ecg)
            my_img_ecg.image = tk_image
            my_img_ecg.configure(image=tk_image)
            ave_hr = heart_rate_normalization(raw_data)
            message = f"The estimated heart rate is \n"
            message += f"{ave_hr} bmp\n"
            output_string.configure(text=message)

    def reset_values():
        """Clears out all the entry fields and response message
        on GUI

        The function is connected to "Reset All" button. After pressing the
        button, it will reset all the entry field to be empty, without manually
        deleting input entry box.

        Returns:
             None

        """
        global filename_ecg
        global filename_medical
        global ave_hr
        name_data.set("")
        id_data.set("")
        file_type.set("")
        filename_ecg = ""
        filename_medical = ""
        ave_hr = 0
        tk_image = load_and_resize_image("Resources/image_holder2.jpeg")
        my_img_ecg.image = tk_image
        my_img_ecg.configure(image=tk_image)
        my_img_medical.image = tk_image
        my_img_medical.configure(image=tk_image)
        output_string.configure(text="")

    def quit_cmd():
        """Closes the GUI window and quits the program.

        The function is linked with the "quit" button. To prevent users
        from accidentally pressing this button, another confirmation is
        required to exit the program. Once the confirmation received, it
        will destroy the GUI interface and close the window. If no further
        confirmation received, it will not execute anything.

        Returns:
            None
        """
        answer = messagebox.askyesno("Quit",
                                     "Do you want to quit the program?")
        if answer:
            if os.path.exists("ecg_test.jpeg"):
                os.remove("ecg_test.jpeg")
            root.destroy()
        return

    root = tk.Tk()
    root.resizable(True, True)
    root.title("Patient GUI")

    ttk.Label(root, text="Name", font=('Courier bold', 16)).\
        grid(column=0, row=1, sticky='e')

    name_data = tk.StringVar()
    name_entry_box = ttk.Entry(root, width=20, textvariable=name_data)
    name_entry_box.grid(column=1, row=1, sticky='w', columnspan=2)

    ttk.Label(root, text="ID", font=('Courier bold', 16)).\
        grid(column=0, row=2, sticky='e')
    id_data = tk.StringVar()
    name_entry_box = ttk.Entry(root, width=20, textvariable=id_data)
    name_entry_box.grid(column=1, row=2, sticky='w', columnspan=2)

    ttk.Label(root, text="Filetype", font=('Courier bold', 16)).\
        grid(column=0, row=3, sticky='e')
    file_type = tk.StringVar()
    combo_box = ttk.Combobox(root, textvariable=file_type)
    combo_box["values"] = ("Medical image (*.jpg / jpeg)",
                           "Raw ECG data (*.csv)")
    combo_box.state(["readonly"])
    combo_box.grid(column=1, row=3, sticky='w', columnspan=2)

    ttk.Label(root, text="Medical Image",
              font=('Courier bold', 26), foreground='green').\
        grid(column=1, row=6, sticky='s')
    tk_image_medical = load_and_resize_image("Resources/image_holder2.jpeg")
    my_img_medical = ttk.Label(root, image=tk_image_medical)
    my_img_medical.grid(column=1, row=5, sticky="w")

    ttk.Label(root, text="ECG Image",
              font=('Courier bold', 26), foreground='blue').\
        grid(column=4, row=6, sticky='s')
    tk_image_ecg = load_and_resize_image("Resources/image_holder2.jpeg")
    my_img_ecg = ttk.Label(root, image=tk_image_ecg)
    my_img_ecg.grid(column=4, row=5, sticky="w")

    change_picture_btn = ttk.Button(root, text="Select Files",
                                    command=change_picture_cmd)
    change_picture_btn.grid(column=3, row=3)

    ok_button = ttk.Button(root, text="Upload", command=ok_button_cmd)
    ok_button.grid(column=5, row=3)

    reset_button = ttk.Button(text="Reset All", command=reset_values)
    reset_button.grid(column=8, row=1, sticky='w')

    quit_button = ttk.Button(root, text="Quit", command=quit_cmd)
    quit_button.grid(column=8, row=8)

    output_string = ttk.Label(root)
    output_string.configure(font=("Courier", 18), foreground="red")
    output_string.grid(column=8, row=5, columnspan=2)

    root.mainloop()


if __name__ == '__main__':
    design_window()
