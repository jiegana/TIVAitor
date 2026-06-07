from core.models.base_model import BasePKModel
from core.patient import Patient

class PropofolMarsh(BasePKModel):
    """
    The original Marsh model, as implemented in the Diprifusor TCI pump.
    Parameters sourced from Seo et al., 2013 (Table 1).
    """
    def __init__(self):
        super().__init__()
        self.name = "Marsh (Diprifusor)"
        self.drug_name = "Propofol"

    def calculate_parameters(self):
        wt = self.patient.weight_kg
        V1 = 0.228 * wt  # Liters
        
        # Micro-constants directly from the Diprifusor manufacturer
        self.params = {
            'V1': V1,
            'k10': 0.119,
            'k12': 0.114,
            'k21': 0.055,
            'k13': 0.042,
            'k31': 0.003,
            'ke0': 0.26  
        }


class PropofolModifiedMarsh(BasePKModel):
    """
    The Modified Marsh model, as implemented in the Base Primea TCI pump.
    Parameters sourced from Seo et al., 2013 (Table 1).
    """
    def __init__(self):
        super().__init__()
        self.name = "Modified Marsh (Base Primea)"
        self.drug_name = "Propofol"

    def calculate_parameters(self):
        wt = self.patient.weight_kg
        V1 = 0.228 * wt  # Liters
        
        # Micro-constants directly from the Base Primea manufacturer
        self.params = {
            'V1': V1,
            'k10': 0.119,
            'k12': 0.112,  # Slightly different from Diprifusor
            'k21': 0.055,
            'k13': 0.042,
            'k31': 0.003,
            'ke0': 1.21    # The major difference! Faster equilibration.
        }