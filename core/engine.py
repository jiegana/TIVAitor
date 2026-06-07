import numpy as np
from scipy.integrate import solve_ivp

def pk_ode(t, y, params, infusion_rate_mg_min):
    """
    The ODEs for a 3-compartment model + effect site.
    y = [C1, C2, C3, Ce] (Concentrations in µg/mL)
    """
    C1, C2, C3, Ce = y
    V1 = params['V1']
    k10, k12, k21, k13, k31, ke0 = params['k10'], params['k12'], params['k21'], params['k13'], params['k31'], params['ke0']
    
    dC1_dt = -(k10 + k12 + k13) * C1 + k21 * C2 + k31 * C3 + (infusion_rate_mg_min / V1)
    dC2_dt = k12 * C1 - k21 * C2
    dC3_dt = k13 * C1 - k31 * C3
    dCe_dt = ke0 * (C1 - Ce)
    
    return [dC1_dt, dC2_dt, dC3_dt, dCe_dt]

def run_simulation(model, events, duration_min):
    """
    Runs the PK simulation using an Event Timeline (Chunking method).
    """
    params = model.get_parameters()
    V1 = params['V1']
    
    # 1. Initial state: Patient is completely drug-free
    y_current = [0.0, 0.0, 0.0, 0.0] # [C1, C2, C3, Ce]
    t_current = 0.0
    current_infusion_rate = 0.0
    
    # We will collect the data from all "chunks" here
    all_t = []
    all_y = [[], [], [], []] 
    
    # Sort events by time just in case the user mixed them up
    sorted_events = sorted(events, key=lambda e: e['time'])
    
    # Add a final "dummy" event at the end to ensure we simulate until the very end
    sorted_events.append({'time': duration_min, 'type': 'end'})
    
    # 2. Loop through the timeline
    for event in sorted_events:
        t_event = event['time']
        
        # If the event is in the future, we need to simulate the "chunk" of time up to it
        if t_event > t_current:
            t_span = (t_current, t_event)
            # Calculate how many data points we need (1 point every 0.1 minutes)
            num_points = max(2, int((t_event - t_current) * 10))
            t_eval = np.linspace(t_current, t_event, num_points)
            
            # Solve the ODE for this specific chunk
            sol = solve_ivp(
                fun=pk_ode,
                t_span=t_span,
                y0=y_current, # Start where the last chunk left off!
                args=(params, current_infusion_rate),
                t_eval=t_eval,
                method='BDF'
            )
            
            # Save the results of this chunk
            if len(all_t) == 0:
                all_t.extend(sol.t)
                for i in range(4): all_y[i].extend(sol.y[i])
            else:
                # Skip the first point (sol.t[1:]) to avoid duplicating the exact same timestamp
                all_t.extend(sol.t[1:])
                for i in range(4): all_y[i].extend(sol.y[i][1:])
            
            # Update our "current state" to the very last point of this chunk
            y_current = [sol.y[0][-1], sol.y[1][-1], sol.y[2][-1], sol.y[3][-1]]
            t_current = t_event
            
        # 3. APPLY THE EVENT (The train has stopped at the station)
        if event['type'] == 'bolus':
            dose = event['dose_mg']
            # A bolus instantly mixes into the central compartment (V1)
            y_current[0] += dose / V1 
            
        elif event['type'] in ['infusion', 'stop']:
            # Update the pump's rate for the next chunk
            # 'stop' events have rate_mg_min = 0.0
            current_infusion_rate = event['rate_mg_min']

    # 4. Format the output to look exactly like the old 'sol' object 
    # so our web interface doesn't break when we update it later!
    class SimulationResult:
        pass
    
    res = SimulationResult()
    res.t = np.array(all_t)
    res.y = np.array(all_y)
    return res


# --- Let's test the Event Timeline! ---
if __name__ == "__main__":
    from core.patient import Patient
    from core.models.propofol import PropofolModifiedMarsh
    
    print("Testing the Event Timeline Engine...")
    
    # 1. Create patient and model
    my_patient = Patient(age=40, height_cm=175, weight_kg=70, sex='M')
    model = PropofolModifiedMarsh()
    model.set_patient(my_patient)
    
    # 2. Define a realistic OR scenario
    # Induction: 150mg bolus + start infusion at 600mg/hr (10 mg/min)
    # Stimulus at 5 min: 50mg bolus
    # Maintenance at 10 min: drop infusion to 300mg/hr (5 mg/min)
    # Wake up at 30 min: stop infusion
    timeline = [
        {'time': 0, 'type': 'bolus', 'dose_mg': 150},
        {'time': 0, 'type': 'infusion', 'rate_mg_min': 10.0},
        {'time': 5, 'type': 'bolus', 'dose_mg': 50},
        {'time': 10, 'type': 'infusion', 'rate_mg_min': 5.0},
        {'time': 30, 'type': 'infusion', 'rate_mg_min': 0.0}
    ]
    
    # 3. Run the simulation for 60 minutes
    results = run_simulation(model, timeline, duration_min=60)
    
    # 4. Print the results at key moments
    print(f"\nTime (min) | Plasma C1 (µg/mL) | Effect Site Ce (µg/mL)")
    print("-" * 55)
    
    for t_target in [0, 2, 5, 5.1, 10, 30, 45]:
        idx = np.argmin(np.abs(results.t - t_target))
        c1 = results.y[0][idx]
        ce = results.y[3][idx]
        print(f"   {t_target:4.1f}   |      {c1:5.2f}       |        {ce:5.2f}")