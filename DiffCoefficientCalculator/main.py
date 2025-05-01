# GITT Analysis Tool
# Made by: Mirzaei
# Last updated: sep 2023
# For analyzing Galvanostatic Intermittent Titration Technique data
# Note: Still need to add proper error handling!

import tkinter as tk  # for the GUI stuff
from tkinter import filedialog, messagebox
import pandas as pd  # handling the excel files
import numpy as np   # for calculations
import matplotlib.pyplot as plt

def pick_file():
    """
    Opens up a file browser to grab the Excel file
    Been using this method for a while, works fine for most cases
    """
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx *.xls")],  # including xls for backwards compatibility
        title="Where's your GITT data?"
    )
    file_input.delete(0, tk.END)
    file_input.insert(0, file_path)

def start_analysis():
    """
    Main function that does all the heavy lifting
    TODO: Break this into smaller functions maybe?
    """
    try:
        # Get all our input values - might need validation later
        sample_mass = float(mass_input.get())
        molar_volume = float(vm_input.get())
        mol_mass = float(molmass_input.get())
        elec_area = float(area_input.get())
        pulse_len = float(tau_input.get())
        data_file = file_input.get()
        
        # Basic checks
        if not data_file:
            messagebox.showerror("Hold up!", "Need an Excel file first!")
            return

        # Load up the data
        print("Reading data...") # helpful for debugging
        data = pd.read_excel(data_file)

        # Make sure we've got the right columns
        needed_cols = ['es', 'etau']
        if not all(col in data.columns for col in needed_cols):
            messagebox.showerror("Data Problem", 
                "Your Excel file needs 'es' and 'etau' columns!\nCheck the template if needed.")
            return

        # Pull out what we need
        steady_state_v = data['es']
        trans_v = data['etau']

        # The big calculation
        # Breaking it down into steps - easier to debug this way
        # D = 4/pi/tau * (mVm/MA)^2 * (Es/Etau)^2
        
        geom_term = ((sample_mass * molar_volume) / (mol_mass * elec_area)) ** 2
        voltage_term = (steady_state_v / trans_v) ** 2
        time_term = 4 / (np.pi * pulse_len)
        
        # Put it all together
        diffusion_coef = time_term * geom_term * voltage_term
        
        # Save the results back to our dataframe
        data['D_calculated'] = diffusion_coef

        # Plotting time!
        plt.style.use('default')  # clean style
        fig = plt.figure(figsize=(10, 6))
        plt.plot(diffusion_coef, 'b.-', linewidth=1.5, markersize=4, 
                label='Diffusion Coefficient')
        
        plt.title('GITT Analysis Results', pad=15)
        plt.xlabel('Measurement Number')
        plt.ylabel('Diffusion Coefficient (D)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='best')
        
        # Make it pretty
        plt.tight_layout()
        
        # Save the plot first
        plt.savefig('GITT_results.png', dpi=300, bbox_inches='tight')
        plt.show()

        # Now save the data
        save_file = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[("Excel files", "*.xlsx")],
            title="Save your results"
        )
        if save_file:
            data.to_excel(save_file, index=False)
            messagebox.showinfo("Success!", f"Data saved to:\n{save_file}")

    except ValueError as ve:
        messagebox.showerror("Input Error", "Check your numbers - something's not right!")
    except Exception as e:
        messagebox.showerror("Oops!", f"Something went wrong:\n{str(e)}")

# GUI Setup
# Using a simple layout - might make it fancier later
root = tk.Tk()
root.title("GITT Analysis Tool v1.0")

# File selection
tk.Label(root, text="Data File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
file_input = tk.Entry(root, width=50)  # nice and wide for long paths
file_input.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=pick_file).grid(row=0, column=2, padx=5, pady=5)

# All our input parameters
# These defaults worked well last time
tk.Label(root, text="Sample mass (m) [g]:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
mass_input = tk.Entry(root)
mass_input.grid(row=1, column=1, padx=5, pady=5, sticky="w")
mass_input.insert(0, "0.1")

tk.Label(root, text="Molar volume (VM) [cm³/mol]:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
vm_input = tk.Entry(root)
vm_input.grid(row=2, column=1, padx=5, pady=5, sticky="w")
vm_input.insert(0, "20.0")

tk.Label(root, text="Molar mass (M) [g/mol]:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
molmass_input = tk.Entry(root)
molmass_input.grid(row=3, column=1, padx=5, pady=5, sticky="w")
molmass_input.insert(0, "50.0")

tk.Label(root, text="Electrode area (A) [cm²]:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
area_input = tk.Entry(root)
area_input.grid(row=4, column=1, padx=5, pady=5, sticky="w")
area_input.insert(0, "1.0")

tk.Label(root, text="Pulse duration (τ) [s]:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
tau_input = tk.Entry(root)
tau_input.grid(row=5, column=1, padx=5, pady=5, sticky="w")
tau_input.insert(0, "100.0")

# The big green button
analyze_button = tk.Button(root, text="Run Analysis!", command=start_analysis,
                         bg="#4CAF50", fg="white", width=20, height=2)
analyze_button.grid(row=6, column=1, pady=20)

# Let's rock and roll
root.mainloop()

"""
TODO List:
- Add input validation
- Maybe add a progress bar for big files
- Save settings between runs?
- Add option to customize plot
- Clean up the GUI layout
- Add help tooltips
"""
