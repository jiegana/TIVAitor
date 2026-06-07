from core.patient import Patient

class BasePKModel:
    def __init__(self):
        # These variables will be shared by ALL drug models
        self.patient = None
        self.name = "Base Model"
        self.drug_name = "Unknown Drug"
        self.params = {} # This dictionary will hold V1, k10, etc.

    def set_patient(self, patient: Patient):
        """Assigns a patient to this model."""
        self.patient = patient
        # Every time the patient changes, we must recalculate the parameters!
        self.calculate_parameters()

    def calculate_parameters(self):
        """This is a placeholder. Specific models MUST overwrite this."""
        raise NotImplementedError("Subclasses must implement this method.")

    def get_parameters(self) -> dict:
        """Returns the PK parameters (V1, k10, etc.) for the current patient."""
        if self.patient is None:
            raise ValueError("No patient assigned to this model!")
        return self.params