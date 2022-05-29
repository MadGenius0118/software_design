from pymodm import MongoModel, fields


class Patient(MongoModel):
    """ Database format for a Patient Record

    This class defines the MongoModel database entry for the Patient database.
    The fields are self-descriptive.  It is used for accessing the MongoDB
    database through the PyMODM package.

    """
    name = fields.CharField()
    medical_record_number = fields.IntegerField(primary_key=True)
    medical_image = fields.ListField()
    ecg_image = fields.ListField()
    heart_rate = fields.ListField()
    timestamp = fields.ListField()
