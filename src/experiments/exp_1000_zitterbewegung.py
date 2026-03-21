import numpy as np

def calculate_amplitudes(delta_phi, parity):
    """
    Calculates the probability distribution of a particle based on its 
    phase alignment with the T3d vacuum geometry.
    """
    # Stickiness (Residence Probability): Destructive interference reflects probability back to t_n0
    p_stay = np.sin(delta_phi / 2)**2
    
    # Movement: Constructive interference allows probability to flow into the active vectors
    p_move_total = np.cos(delta_phi / 2)**2
    
    # The flow is divided equally among the 3 active neighbors (Bipartite Parity Rule)
    p_each_neighbor = p_move_total / 3.0

    print(f"--- Tick Parity: {'EVEN (RGB Active)' if parity == 0 else 'ODD (CMY Active)'} ---")
    print(f"Nucleus (t_n0) Probability : {p_stay:.4f}")
    
    if parity == 0:
        print(f"  V1 (Red)   Probability : {p_each_neighbor:.4f}")
        print(f"  V2 (Green) Probability : {p_each_neighbor:.4f}")
        print(f"  V3 (Blue)  Probability : {p_each_neighbor:.4f}")
        print(f"  -V1/-V2/-V3 (CMY)      : 0.0000 (Blocked by Parity)")
    else:
        print(f"  V1/V2/V3 (RGB)         : 0.0000 (Blocked by Parity)")
        print(f"  -V1 (Cyan)    Probability : {p_each_neighbor:.4f}")
        print(f"  -V2 (Magenta) Probability : {p_each_neighbor:.4f}")
        print(f"  -V3 (Yellow)  Probability : {p_each_neighbor:.4f}")
        
    # Verifying Rule 2: A=1 Conservation
    total_a = p_stay + (p_each_neighbor * 3)
    print(f"Total Probability (A)      : {total_a:.4f}\n")

def run_zitterbewegung_sim():
    print("Experiment 01: Zitterbewegung and Phase-Induced Mass\n")
    
    # Test 1: The Photon (Perfect Phase Alignment)
    print("=== TEST 1: The Photon (Delta Phi = 0) ===")
    calculate_amplitudes(delta_phi=0.0, parity=0)
    
    # Test 2: The Massive Particle (Intermediate Phase Mismatch)
    # We use pi/2 to simulate a particle with 50% stickiness (mass)
    print("=== TEST 2: The Massive Particle (Delta Phi = pi/2) ===")
    calculate_amplitudes(delta_phi=np.pi/2, parity=0) # Tick 1: Breathes out to RGB
    calculate_amplitudes(delta_phi=np.pi/2, parity=1) # Tick 2: Breathes out to CMY

if __name__ == "__main__":
    run_zitterbewegung_sim()