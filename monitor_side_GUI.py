import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
from tkinter import filedialog, messagebox, simpledialog


from client import get_patient_from_server
from client import b64_string_to_file
from client import get_patient_latest
from client import get_patient_id_list

from patient_side_GUI import load_and_resize_image


def design_window():
    """Creates the main GUI window for the Monitoring side

    A GUI window is created that is the main interface for the patient
    monitoring station. It accepts information from the user comboboxes
    where it allows the user to select the patient ID, name of Available
    ECG image and name of Available medical image from the dynamically
    updating drop-down lists. The interface is able to display three images
    in a row: selected medical image, selected ECG image and the patient's
    latest ECG image, as well as an output text of summarized patient
    information on the GUI. Also, it allows the user to save the selected
    images locally to any desired directory as any desired filename, based
    on the user input values from the dialog windows.

    Everytime the user make an selection in ID combobox, the latest ECG image
    of that patient will show in the widget labeled "Latest ECG", along with
    a text of patient information including patient name, id, latest heart
    rate and latest timestamp on the right-hand side of GUI.
    If the patient has no ECG images available, a place-holder image showing
    "No image available" will be displayed in the place of the Latest ECG
    widget, and the latest heart rate and timestamp information will be
    shown as Unknown in the output text.
    At this moment, the Available ECG and medical image comboboxes are
    defaulted as empty, and another place-holder image from Resources folder
    are displayed in the places of medical and selected ECG image widgets.
    In this way, upon each new selection of patient ID, any information
    from the previous patient on the interface gets replaced with the
    information from the new patient.

    After the user selects a medical image name from the drop-down list of
    the Available medical image combobox, the corresponding image from
    the images folder will be decoded and displayed in the left widget
    labeled "Medical Image" on GUI.
    Similarly, when the user makes a selection in the drop-down list of
    the Available ECG image combobox, the corresponding image with the
    selected index will be get from the server database, and then decoded
    and displayed in the middle widget labeled "Selected ECG Image" on GUI.

    Upon hitting any of the "Download" buttons under the images widgets,
    a directory selection window will display for the user to choose the
    local directory to save this image. After selecting the directory,
    a dialog window will display for the user to enter a filename for the
    image to be saved. If any information is missing and the image cannot
    be successfully saved, a warning messagebox will appear indicating
    "No image can be saved".

    Upon hitting the "Quit" button, a confirmation window will pop up to
    prevent accidental pressing. If "No" is selected, it goes back to the
    interface; if "Yes" is selected, the window closes.

    Returns:
        None

        """

    def save_medical():
        """Downloads selected medical image to be saved locally

        The function is connected to the "Download" button under the
        Medical Image label widget on the GUI, and it uses Tkinter dialogs
        and message box to get values from the user.

        When the patient number is chosen, and the path exists for the
        selected medical image (which is recovered from b64-string and
        named as "medical.jpeg" in callback function medical_past),
        a click on the Download button under the Medical Image widget
        will create a directory selection window for the user to select
        a local folder to save the image. After directory is selected, a
        dialog window will pop up to ask the user for a filename to be saved.
        With the specified  filename, the function opens the image and saves
        it to the designated directory.
        If any of the image information is unavailable, the function will
        create a warning message box indicating that no image can be saved.

        Returns:
            None

        """
        if (id_data.get() != "") and (os.path.exists("medical.jpeg")) and \
                (combo_box_medical.get() != ""):
            directory = filedialog.askdirectory(initialdir=os.getcwd(),
                                                title="Please "
                                                      "select a folder:")
            if directory != "":
                answer = simpledialog.askstring(f"Input",
                                                "Please enter name "
                                                "to be saved as")
                if answer != "":
                    filename = directory + "/" + answer + ".jpeg"
                    img = Image.open("medical.jpeg")
                    img.save(filename)
                return
            return
        else:
            messagebox.showinfo("warning", f"No image can be saved")

    def medical_past(event):
        """Decodes and displays a past medical image on GUI

        This is a combobox callback function that is bound to the medical
        combobox virtual event of an user selection of an available medical
        image from the drop-down list. It is called in the function
        get_patient_medical().

        The function reads the patient number from the id combobox and calls
        the get_patient_from_server function to get that patient's dictionary
        from the server database. It also reads the index of the selected
        option in medical image combobox, and uses that to locate the image
        string in the "medical_image" entries of patient dictionary. Then,
        the function calls the b64_string_to_file function to convert the b64-
        string into image file with filename "medical.jpeg", and then rescales
        and displays the image on GUI by calling the load_and_resize_image
        function. It also stores the image as a label widget property to
        prevent garbage collection and loss of image.

        Returns:
            None

        """
        index = combo_box_medical.current()
        id = id_data.get()
        patient_dict = get_patient_from_server(id)
        past_medical_image = patient_dict["medical_image"][index]
        b64_string_to_file(past_medical_image, "medical.jpeg")
        tk_medical = load_and_resize_image("medical.jpeg")
        my_img_label_medical.image = tk_medical
        my_img_label_medical.configure(image=tk_medical)

    def get_patient_medical():
        """Configures the drop-down list and event binding for the medical
        image combobox.

        The function first reads the patient id selection and calls the
        get_patient_from_server function to get the corresponding patient
        dictionary. The drop-down options were initiated as an empty list,
        and then populated to have the same length as the list of b64-strings
        under key "medical_image" in that patient's dictionary, following the
        naming convention "medical_image<number>". Then, the list of drop-down
        options is converted to a tuple and configured as selection options
        to display in medical combobox. The function uses the bind() method
        to implement a Tk combobox event binding: when a combobox virtual
        event happens that the user selects an element in the drop-down list
        of medical image combobox, the callback function medical_past is
        actioned and displays the medical image on GUI.

        Returns:
            None

        """
        id = id_data.get()
        if id != "":
            patient_dict = get_patient_from_server(id)
            ecg_list = patient_dict["medical_image"]
            image_index = []
            for i in range(len(ecg_list)):
                image_index.append(f"medical_image{i+1}")
            combo_box_medical.configure(values=tuple(image_index))
            combo_box_medical.bind("<<ComboboxSelected>>", medical_past)

    def ecg_past(event):
        """Decodes and displays a past ECG image on GUI

        This is a combobox callback function that is bound to the ECG
        combobox virtual event of an user selection of an available
        ECG image from the drop-down list. It is called in the function
        get_patient_ecg().

        The function reads the patient number from the id combobox and calls
        the get_patient_from_server function to get that patient's dictionary
        from the server database. If the patient dictionary has no ECG image
        available, the function calls the load_and_resize_image function to
        rescale and display a pre-loaded "no_image.jpeg" image from the
        Resources folder in the place of ECG image widget on GUI. If the key
        "ecg_image" has values, the function reads in the index of the
        selected option from ECG image combobox and uses the index to find
        the image string in "ecg_image" entry of patient dictionary. Then,
        the function calls the b64_string_to_file function to convert the b64-
        string into image file with filename "ecg_past.jpeg", and then rescales
        and displays the image on GUI by calling the load_and_resize_image
        function. It also stores the image as a label widget property to
        prevent garbage collection and loss of image.

        Returns:
            None

        """
        index = combo_box_images.current()
        id = id_data.get()
        patient_dict = get_patient_from_server(id)
        if patient_dict["ecg_image"] == []:
            tk_image = load_and_resize_image("Resources/no_image.jpeg")
            my_img_label_past.image = tk_image
            my_img_label_past.configure(image=tk_image)
            return
        past_ecg_image = patient_dict["ecg_image"][index]
        b64_string_to_file(past_ecg_image, "ecg_past.jpeg")
        tk_image_past = load_and_resize_image("ecg_past.jpeg")
        my_img_label_past.image = tk_image_past
        my_img_label_past.configure(image=tk_image_past)

    def save_ecg_past():
        """Downloads selected ECG image to be saved locally

        The function is connected to the "Download" button under the
        Selecetd ECG Image label widget on the GUI, and it uses Tkinter
        dialogs and message box to get values from the user.

        When the patient number is chosen, and the path exists for the
        selected ECG image (which is recovered from b64-string and
        named as "ecg_past.jpeg" in callback function ecg_past),
        a click on the Download button under the Selected ECG Image widget
        will create a directory selection window for the user to select
        a local folder to save the image. After directory is selected, a
        dialog window will pop up to ask the user for a filename to be saved.
        With the specified  filename, the function opens the image and saves
        it to the designated directory.
        If any of the image information is unavailable, the function will
        create a warning message box indicating that no image can be saved.

        Returns:
            None

        """
        if (id_data.get() != "") and (os.path.exists("ecg_past.jpeg")) and \
                (combo_box_images.get() != ""):
            directory = filedialog.askdirectory(initialdir=os.getcwd(),
                                                title="Please "
                                                      "select a folder:")
            if directory != "":
                answer = simpledialog.askstring(f"Input",
                                                "Please enter name "
                                                "to be saved as")
                if answer != "":
                    filename = directory + "/" + answer + ".jpeg"
                    img = Image.open("ecg_past.jpeg")
                    img.save(filename)
                return
            return
        else:
            messagebox.showinfo("warning", f"No image can be saved")

    def get_patient_ecg():
        """Configures the drop-down list and event binding for the ECG
        image combobox.

        The function first reads the patient id selection and calls the
        get_patient_from_server function to get the corresponding patient
        dictionary. Then, it gets the list of values stored in key "timestamp"
        in the patient dictionary, and converts this list of drop-down options
        to a tuple and configures it into selection options to display in
        ECG image combobox. Then, the function uses the bind() method
        to implement a Tk combobox event binding: when a combobox virtual
        event happens as the user selects an element in the drop-down list of
        ECG image combobox, the callback function ecg_past is actioned and
        displays the ECG image on GUI.

        Returns:
            None

        """
        id = id_data.get()
        if id != "":
            patient_dict = get_patient_from_server(id)
            ecg_timestamp = patient_dict["timestamp"]
            combo_box_images.configure(values=tuple(ecg_timestamp))
            combo_box_images.bind("<<ComboboxSelected>>", ecg_past)
        else:
            return

    def save_current():
        """Downloads the latest ECG image to be saved locally

        The function is connected to the "Download" button under the
        Latest ECG label widget on the GUI, and it uses Tkinter dialogs
        and message box to get values from the user.

        When the patient number is chosen, and the path exists for the
        latest ECG image (which is recovered from b64-string and
        named as "ecg_latest.jpeg" in callback function ecg_latest),
        a click on the Download button under the Latest ECG label widget
        will create a directory selection window for the user to select
        a local folder to save the image. After directory is selected, a
        dialog window will pop up to ask the user for a filename to be saved.
        With the specified  filename, the function opens the image and saves
        it to the designated directory.
        If any of the image information is unavailable, the function will
        create a warning message box indicating that no image can be saved.

        Returns:
            None

        """
        if (id_data.get() != "") and (os.path.exists("ecg_latest.jpeg")):
            directory = filedialog.askdirectory(initialdir=os.getcwd(),
                                                title="Please "
                                                      "select a folder:")
            if directory != "":
                answer = simpledialog.askstring(f"Input",
                                                "Please input your filename")
                if answer != "":
                    filename = directory + "/" + answer + ".jpeg"
                    img = Image.open("ecg_latest.jpeg")
                    img.save(filename)
                return
            return
        else:
            messagebox.showinfo("warning", f"No image can be saved")

    def ecg_latest(event):
        """Decodes and displays the latest ECG image on GUI

        This is a combobox callback function that is bound to the ID combobox
        virtual event of an user selection of an available patient number
        from the drop-down list. It is called by the bind() method in the
        function get_patient_id_cmd.

        Firstly, the function checks if any file named "ecg_latest.jpeg"
        already exists and removes that file if there is any.
        Then, the function reads the patient number from the id combobox
        and calls the get_patient_from_server function to get that patient's
        dictionary from the server database.
        If the patient dictionary has no ECG image available, the function
        calls the load_and_resize_image function to rescale and display a
        pre-loaded "no_image.jpeg" image from the Resources folder in the
        place of Latest ECG image widget on GUI. Also, the function displays
        an output string on the GUI in the format of:

                            "Patient name: John Smith
                             Medical Record Number: 2
                             Latest heart rate: Unknown
                             Latest timestamp: Unknown"

        If the value to key "ecg_image" is non-empty, the function calls the
        get_patient_latest function imported from client.py to get the
        patient information from the patient dictionary including: name, id,
        latest_ecg_image, latest_hr and latest_timestamp. Then, the function
        calls the b64_string_to_file function to convert the b64-string
        object "latest_ecg_image" into an image file with filename
        "ecg_latest.jpeg", and then rescales and displays the image on GUI
        by calling the load_and_resize_image function. It also stores the
        image as a label widget property to prevent garbage collection and
        loss of image. Also, the function displays an output string on the GUI
        in the format of:

                            "Patient name: Ann Ables
                             Medical Record Number: 3
                             Latest heart rate: 80
                             Latest timestamp:  2021-12-05 13:33:18"

        Returns:
            None

        """
        if os.path.exists("ecg_latest.jpeg"):
            os.remove("ecg_latest.jpeg")
        id = id_data.get()
        patient_dict = get_patient_from_server(id)
        if patient_dict["ecg_image"] == []:
            tk_image = load_and_resize_image("Resources/no_image.jpeg")
            my_img_label_latest.image = tk_image
            my_img_label_latest.configure(image=tk_image)
            message = f"Patient name: {patient_dict['name']} \n"
            message += f"Medical Record Number: {id} \n"
            message += f"Latest heart rate: Unknown \n"
            message += f"Latest timestamp: Unknown"
            output_string.configure(text=message)
            return
        name, id_no, latest_ecg_image, latest_hr, latest_timestamp =\
            get_patient_latest(patient_dict)
        b64_string_to_file(latest_ecg_image, "ecg_latest.jpeg")
        tk_image_latest = load_and_resize_image("ecg_latest.jpeg")
        my_img_label_latest.image = tk_image_latest
        my_img_label_latest.configure(image=tk_image_latest)
        message = f"Patient name: {name} \n"
        message += f"Medical Record Number: {id_no} \n"
        message += f"Latest heart rate: {latest_hr} \n"
        message += f"Latest timestamp: {latest_timestamp}"
        output_string.configure(text=message)

    def update_combo():
        """Dynamically updates the options for choices on the GUI

        When the user wants to select a new patient, an historical ECG,
        or a medical image for a patient on the GUI, the choices should
        represent the most recent options on the server. This function is
        to prevent the option choices from being "locked in" based on
        what was available when the client was started. It dynamically
        updates the drop-down options to display on GUI based on periodic
        check (every 5 sec) on patient input, and prints messages of
        "update begins" to keep record of these periodic requests.

        The function reads the patient number from the ID combobox and
        calls the get_patient_from_server function to get that patient's
        dictionary from the server database. If the patient dictionary has
        no ECG image available, the function calls the load_and_resize_image
        function to rescale and display the pre-loaded "no_image.jpeg" image
        from the Resources folder in the place of Latest ECG image widget
        on GUI. Also, the function displays an output string on the GUI
        containing information of patient name, medical record number,
        latest heart rate ('Unknown' if empty) and latest timestamp
        ('Unknown' if empty).
        If the dictionary key "ecg_image" has values, the function calls the
        get_patient_latest function imported from client.py to get the
        patient information from the patient dictionary including: name, id,
        latest_ecg_image, latest_hr and latest_timestamp. Then, the function
        calls the b64_string_to_file function to convert the b64-string
        object "latest_ecg_image" into an image file with filename
        "ecg_latest.jpeg", and then rescales and displays the image on GUI
        by calling the load_and_resize_image function. It also stores the
        image as a label widget property to prevent garbage collection and
        loss of image. Also, the function displays an output string on the GUI
        containing information of patient name, medical record number,
        latest heart rate and latest timestamp.
        Finally, this periodic function reschedules itself when it is done
        working by calling the root.after method. In this way, the latest
        ecg image gets updated every 5000 msec based on any patient database
        changes on the server.

        Returns:
            None

        """
        print("Update begins")
        root.after(5000, update_combo)
        id = id_data.get()
        if id != "":
            patient_dict = get_patient_from_server(id)
            if patient_dict["ecg_image"] == []:
                tk_image = load_and_resize_image("Resources/no_image.jpeg")
                my_img_label_latest.image = tk_image
                my_img_label_latest.configure(image=tk_image)
                message = f"Patient name: {patient_dict['name']} \n"
                message += f"Medical Record Number: {id} \n"
                message += f"Latest heart rate: Unknown \n"
                message += f"Latest timestamp: Unknown"
                output_string.configure(text=message)
                return
            name, id_no, latest_ecg_image, latest_hr, latest_timestamp = \
                get_patient_latest(patient_dict)
            b64_string_to_file(latest_ecg_image, "ecg_latest.jpeg")
            tk_image_latest = load_and_resize_image("ecg_latest.jpeg")
            my_img_label_latest.image = tk_image_latest
            my_img_label_latest.configure(image=tk_image_latest)
            message = f"Patient name: {patient_dict['name']} \n"
            message += f"Medical Record Number: {id} \n"
            message += f"Latest heart rate: {latest_hr} \n"
            message += f"Latest timestamp: {latest_timestamp}"
            output_string.configure(text=message)
            return
        return

    def get_patient_id_cmd():
        """Configures the drop-down list and event binding for the ID
        combobox.

        First, the function checks and removes any existing file named
        "ecg_latest.jpeg". Then, it defaults the selections of Available ECG
        image and Available medical image comboboxes to be empty strings,
        and calls the load_and_resize_image function to display the
        pre-loaded image "image_holder2.jpeg" from Resources folder as
        place holders in the position of Medical Image widget and past
        ECG image widget.
        Then, it calls the get_patient_id_list() function imported from
        client.py to get the list of patient numbers stored in database
        from the server. This list of ID drop-down options is then converted
        to a tuple and configured into selection options of the ID combobox
        on the GUI. Then, the function uses the bind() method to implement
        a Tk combobox event binding: once the user makes a selection from
        the drop-down list of ID combobox, the callback function ecg_latest
        will run and displays all the necessary information on GUI.

        Returns:
            None

        """
        if os.path.exists("ecg_latest.jpeg"):
            os.remove("ecg_latest.jpeg")
        tk_image = load_and_resize_image("Resources/image_holder2.jpeg")
        combo_box_images.set("")
        combo_box_medical.set("")
        my_img_label_past.image = tk_image
        my_img_label_past.configure(image=tk_image)
        my_img_label_medical.image = tk_image
        my_img_label_medical.configure(image=tk_image)
        id_list = get_patient_id_list()
        combo_box.configure(values=tuple(id_list))
        combo_box.bind("<<ComboboxSelected>>", ecg_latest)

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
            if os.path.exists("ecg_past.jpeg"):
                os.remove("ecg_past.jpeg")
            if os.path.exists("ecg_latest.jpeg"):
                os.remove("ecg_latest.jpeg")
            if os.path.exists("medical.jpeg"):
                os.remove("medical.jpeg")
            root.destroy()
        return

    root = tk.Tk()
    root.resizable(True, True)
    root.title("Client GUI")

    ttk.Label(root, text="ID", font=('Courier bold', 16)).\
        grid(column=0, row=2, sticky='e')
    id_data = tk.StringVar()
    combo_box = ttk.Combobox(root, textvariable=id_data,
                             postcommand=get_patient_id_cmd)
    combo_box.state(["readonly"])
    combo_box.grid(column=1, row=2, sticky='w', columnspan=2)

    ttk.Label(root, text="Available ECG image", font=('Courier bold', 16)).\
        grid(column=0, row=3, sticky='e')
    image_data = tk.StringVar()
    combo_box_images = ttk.Combobox(root, textvariable=image_data,
                                    postcommand=get_patient_ecg)
    combo_box_images.state(["readonly"])
    combo_box_images.grid(column=1, row=3, sticky='w', columnspan=2)

    ttk.Label(root, text="Available medical image",
              font=('Courier bold', 16)).grid(column=0, row=4, sticky='e')
    image_medical = tk.StringVar()
    combo_box_medical = ttk.Combobox(root, textvariable=image_medical,
                                     postcommand=get_patient_medical)
    combo_box_medical.state(["readonly"])
    combo_box_medical.grid(column=1, row=4, sticky='w', columnspan=2)

    ttk.Label(root, text="Selected ECG Image", font=('Courier bold', 20),
              foreground='orange').grid(column=2, row=6, sticky='s')
    past_image = load_and_resize_image("Resources/image_holder2.jpeg")
    my_img_label_past = ttk.Label(root, image=past_image)
    my_img_label_past.grid(column=2, row=5, sticky="n")

    download_previous_button = ttk.Button(text="Download",
                                          command=save_ecg_past)
    download_previous_button.grid(column=2, row=7, sticky='n')

    ttk.Label(root, text="Latest ECG", font=('Courier bold', 20),
              foreground='blue').grid(column=3, row=6, sticky='s')
    tk_image = load_and_resize_image("Resources/image_holder2.jpeg")
    my_img_label_latest = ttk.Label(root, image=tk_image)
    my_img_label_latest.grid(column=3, row=5, sticky="n")

    download_current_button = ttk.Button(text="Download", command=save_current)
    download_current_button.grid(column=3, row=7, sticky='n')

    ttk.Label(root, text="Medical Image", font=('Courier bold', 20),
              foreground='green').grid(column=0, row=6, sticky='s')
    tk_image_medical = load_and_resize_image("Resources/image_holder2.jpeg")
    my_img_label_medical = ttk.Label(root, image=tk_image_medical)
    my_img_label_medical.grid(column=0, row=5, sticky="n")

    download_medical_button = ttk.Button(text="Download", command=save_medical)
    download_medical_button.grid(column=0, row=7, sticky='n')

    output_string = ttk.Label(root)
    output_string.configure(font=("Courier", 18), foreground="black")
    output_string.grid(column=6, row=3, columnspan=3)

    quit_button = ttk.Button(root, text="Quit", command=quit_cmd)
    quit_button.grid(column=10, row=2)

    root.after(5000, update_combo)
    root.mainloop()


if __name__ == '__main__':
    design_window()
