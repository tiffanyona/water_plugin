import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

class DataEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Entry App")

        # Create variables to store input values
        self.mouse_id_var = tk.StringVar()
        self.weights_var = tk.StringVar()
        self.date_var = tk.StringVar(value=self.get_current_date())
        self.session_var = tk.StringVar(value="After session")
        self.condition_var = tk.StringVar(value="After session")
        self.collected_water_var = tk.StringVar()
        self.suggested_water_var = tk.StringVar()
        self.summary_text = tk.StringVar()

        # Create labels and entry fields
        date_label = tk.Label(root, text="Date:", bg="grey", fg="white", padx=10, pady=5, anchor='w')
        date_label.grid(row=0, column=0, columnspan=2, sticky=tk.W + tk.E)

        ttk.Label(root, text="Mouse ID:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Entry(root, textvariable=self.mouse_id_var, validate="key", validatecommand=(self.root.register(self.validate_mouse_id), "%P")).grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(root, text="Weights:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Entry(root, textvariable=self.weights_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(root, text="Session:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        session_combobox = ttk.Combobox(root, textvariable=self.session_var, values=["Before session", "After session", "Rest day", "Baseline weight"])
        session_combobox.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)
        session_combobox.set("After session")

        ttk.Label(root, text="Condition:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        condition_combobox = ttk.Combobox(root, textvariable=self.condition_var, values=["Before session", "After session", "Rest day", "Baseline weight"])
        condition_combobox.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)
        condition_combobox.set("After session")

        ttk.Label(root, text="Collected water during the session (mL):").grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)
        self.collected_water_entry = ttk.Entry(root, textvariable=self.collected_water_var, validate="key", validatecommand=(self.root.register(self.validate_float), "%P"))
        self.collected_water_entry.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Create a button to submit data
        ttk.Button(root, text="Submit", command=self.submit_data).grid(row=6, column=0, columnspan=2, pady=10)

        # Create a suggested water label
        ttk.Label(root, text="Suggested water (mL):").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(root, textvariable=self.suggested_water_var, font=('Arial', 12)).grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)

        # Create a summary label
        ttk.Label(root, textvariable=self.summary_text, font=('Arial', 12)).grid(row=8, column=0, columnspan=3, pady=10)

        # Create a canvas for plotting
        self.canvas = tk.Canvas(root)
        self.canvas.grid(row=0, column=3, rowspan=8, padx=10)

        # Plot button
        ttk.Button(root, text="Plot", command=self.plot_data).grid(row=8, column=3, padx=10, pady=5)

        # Load existing water log (if any)
        self.load_water_log()

    def submit_data(self):
        # ... (previous code remains unchanged)

        # Calculate suggested water
        self.calculate_suggested_water()

        # Display summary
        self.display_summary(df)

        # Plot the data
        self.plot_data()

    def toggle_collected_water(self):
        condition = self.condition_var.get()
        if condition == "After session":
            self.collected_water_entry.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
            self.collected_water_label.grid(row=5, column=2, sticky=tk.W)
        else:
            self.collected_water_entry.grid_remove()
            self.collected_water_label.grid_remove()

    def get_current_date(self):
        return datetime.now().strftime("%Y-%m-%d")
    
    def validate_mouse_id(self, new_value):
        return new_value.isdigit() and len(new_value) <= 6
    
    def toggle_manual_input(self):
        if self.manual_input_var.get():
            date_entry = ttk.Entry(self.root, textvariable=self.date_var)
            date_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
            date_entry.focus_set()
        else:
            self.date_var.set(self.get_current_date())
            try:
                date_entry.destroy()
            except AttributeError:
                pass
            
    def plot_data(self):
        try:
            water_log = pd.read_csv("water_log_VR.csv")

            mouse_id = self.mouse_id_var.get()
            filtered_df = water_log[water_log['Mouse ID'] == mouse_id]

            if filtered_df.empty:
                messagebox.showwarning("Warning", f"No data found for Mouse ID {mouse_id}. Cannot plot.")
                return

            # Plotting
            self.canvas.delete("all")

            plt.figure(figsize=(8, 4))
            plt.plot(filtered_df['Date'], filtered_df['Weights'], marker='o', linestyle='', markersize=8, label='Weight')

            baseline_df = filtered_df[filtered_df['Condition'] == 'Baseline weight']
            plt.plot(baseline_df['Date'], baseline_df['Weights'], marker='o', linestyle='', markersize=8, label='Baseline weight', color='green')

            after_session_df = filtered_df[filtered_df['Condition'] == 'After session']
            plt.plot(after_session_df['Date'], after_session_df['Weights'], marker='s', linestyle='', markersize=8, label='After session', color='blue')

            rest_day_df = filtered_df[filtered_df['Condition'] == 'Rest day']
            plt.plot(rest_day_df['Date'], rest_day_df['Weights'], marker='x', linestyle='', markersize=8, label='Rest day', color='red')

            plt.title(f"Weight Plot for Mouse ID {mouse_id}")
            plt.xlabel("Date")
            plt.ylabel("Weight")
            plt.legend()
            plt.grid(True)

            # Convert the plot to a PhotoImage object
            plt.savefig("plot.png")
            plt.close()

            # Display the plot on the canvas
            img = tk.PhotoImage(file="plot.png")
            self.canvas.config(width=img.width(), height=img.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.canvas.image = img  # Keep a reference to avoid garbage collection

        except FileNotFoundError:
            print("No existing water log found.")

    def validate_float(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def display_summary(self, df):
        summary_text = f"Summary:\n\n{df.to_string(index=False)}"
        self.summary_text.set(summary_text)

    def accept_summary(self):
        self.summary_text.set("")  # Clear the summary
        self.mouse_id_var.set("")  # Clear the input fields
        self.weights_var.set("")
        self.date_var.set(self.get_current_date())
        self.session_var.set("After session")
        self.condition_var.set("After session")
        self.collected_water_var.set("")
        self.suggested_water_var.set("")  # Clear suggested water

    def load_water_log(self):
        try:
            df = pd.read_csv("water_log_VR.csv")
            print("Loaded water log:")
            print(df)
        except FileNotFoundError:
            print("No existing water log found.")

    def append_to_water_log(self, df):
        try:
            existing_df = pd.read_csv("water_log_VR.csv")
            updated_df = pd.concat([existing_df, df], ignore_index=True)
        except FileNotFoundError:
            updated_df = df

        updated_df.to_csv("water_log_VR.csv", index=False)
        print("Water log updated.")

    def calculate_suggested_water(self):
        # Load existing water log if available
        try:
            df = pd.read_csv("water_log_VR.csv")
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Mouse ID', 'Date', 'Weights', 'Session', 'Condition', 'Collected Water'])

        # Filter the DataFrame based on the current mouse ID
        current_mouse_id = int(self.mouse_id_var.get())
        current_mouse_df = df[df['Mouse ID'] == current_mouse_id]

        # Check if the DataFrame is not empty
        if not current_mouse_df.empty:
            # Filter the DataFrame for the "Baseline weight" condition
            baseline_df = current_mouse_df[current_mouse_df['Condition'] == 'Baseline weight']

            # Check if the baseline DataFrame is not empty
            if not baseline_df.empty:
                # Calculate the target weight
                target_weight = baseline_df['Weights'].mean() * 0.8

                # Filter the DataFrame for the current condition
                current_condition_df = current_mouse_df[current_mouse_df['Condition'] == self.condition_var.get()]

                # Get the weight for the last entry in the current condition
                if not current_condition_df.empty:
                    current_weight = current_condition_df['Weights'].iloc[-1]

                    # Calculate suggested water
                    suggested_water = max(0, target_weight - current_weight)

                    # Update the suggested_water_var
                    self.suggested_water_var.set(f"{suggested_water:.2f} mL")
                else:
                    # If the current condition DataFrame is empty, set suggested water to 0
                    self.suggested_water_var.set("0.00 mL")
            else:
                # If the baseline DataFrame is empty, show an error message
                messagebox.showerror("Error", "There is no baseline weight for this mouse. Can't give a suggested water recommendation.")
                self.suggested_water_var.set("Error")
        else:
            # If the current mouse DataFrame is empty, set suggested water to 0
            self.suggested_water_var.set("0.00 mL")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = DataEntryApp(root)
    root.mainloop()
