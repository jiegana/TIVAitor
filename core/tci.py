import numpy as np

def generate_plasma_tci_events(model, target_conc, duration_min):
    """
    Generates an Event Timeline for Plasma Target Controlled Infusion (TCI).
    Uses the exact analytical solution to maintain a constant plasma concentration.
    """
    params = model.get_parameters()
    V1 = params['V1']
    k10, k12, k21, k13, k31 = params['k10'], params['k12'], params['k21'], params['k13'], params['k31']
    
    events = []
    
    # 1. The Initial Bolus (t = 0)
    # To instantly reach the target in the central compartment (V1)
    bolus_dose = target_conc * V1
    events.append({
        'time': 0.0, 
        'type': 'bolus', 
        'dose_mg': bolus_dose, 
        'rate_mg_min': 0.0, 
        'display': f'TCI Bolus {bolus_dose:.1f} mg (Target Cp: {target_conc} µg/mL)'
    })
    
    # 2. The Maintenance Infusion (Calculated every 1 minute)
    # We generate an event every minute to update the pump rate
    for t in range(1, int(duration_min) + 1):
        # The exact math formula to maintain constant Cp
        rate_mg_min = V1 * target_conc * (k10 + k12 * np.exp(-k21 * t) + k13 * np.exp(-k31 * t))
        
        events.append({
            'time': float(t),
            'type': 'infusion',
            'dose_mg': 0.0,
            'rate_mg_min': rate_mg_min,
            'display': f'TCI Maintenance @ {t} min: {rate_mg_min * 60:.1f} mg/hr'
        })
        
    return events