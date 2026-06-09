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
    
    # --- FIX 1: Start with the initial zero state so the graph begins at 0 ---
    all_t = [0.0]
    all_y = [[0.0], [0.0], [0.0], [0.0]] 
    
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
            num_points = max(2, int((t_event - t_current) * 10))
            t_eval = np.linspace(t_current, t_event, num_points)
            
            sol = solve_ivp(
                fun=pk_ode,
                t_span=t_span,
                y0=y_current, 
                args=(params, current_infusion_rate),
                t_eval=t_eval,
                method='BDF'
            )
            
            # --- FIX 2: Always include sol.t[0] to capture the post-event state ---
            # By including the exact same timestamp, Plotly will draw a perfect vertical line for boluses!
            all_t.extend(sol.t)
            for i in range(4): 
                all_y[i].extend(sol.y[i])
            
            # Update our "current state" to the very last point of this chunk
            y_current = [sol.y[0][-1], sol.y[1][-1], sol.y[2][-1], sol.y[3][-1]]
            t_current = t_event
            
        # 3. APPLY THE EVENT (The train has stopped at the station)
        if event['type'] == 'bolus':
            dose = event['dose_mg']
            y_current[0] += dose / V1 
            
        elif event['type'] in ['infusion', 'stop']:
            current_infusion_rate = event['rate_mg_min']

    # 4. Format the output to look exactly like the old 'sol' object 
    class SimulationResult:
        pass
    
    res = SimulationResult()
    res.t = np.array(all_t)
    res.y = np.array(all_y)
    return res