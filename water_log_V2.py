import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkFont
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DataEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Water log VR")

        # Set font for the entire interface
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=18)
    
        # Create a style for the dropdown
        self.dropdown_style = ttk.Style()
        self.dropdown_style.configure('TCombobox', font=('Helvetica', 18))  # Set the font size as needed

        # Set default values
        self.date_var = tk.StringVar()
        self.mouse_id_var = tk.StringVar()
        self.condition_var = tk.StringVar(value="After session")
        self.weight_var = tk.StringVar()
        self.water_var = tk.StringVar()

        # Create and pack widgets
        self.create_widgets()
        
        # Load or create dataframe
        self.df = self.load_dataframe()
    
        # Create Figure and Axes for the plot
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def create_widgets(self):
        self.label_date = tk.Label(self.root, text="Date:")
        self.label_date.grid(row=0, column=0, sticky="e")

        self.get_current_date()
        self.entry_date = tk.Entry(self.root, textvariable=self.date_var, state='readonly')
        self.entry_date.grid(row=0, column=1, sticky="w")
        self.entry_date.config(font=("Helvetica", 18))

        # Mouse ID
        self.label_mouse_id = tk.Label(self.root, text="Mouse ID:")
        self.label_mouse_id.grid(row=1, column=0, sticky="e")

        self.entry_mouse_id = tk.Entry(self.root, textvariable=self.mouse_id_var)
        self.entry_mouse_id.grid(row=1, column=1, sticky="w")
        self.entry_mouse_id.config(font=("Helvetica", 18))
    
        # Condition
        self.label_condition = tk.Label(self.root, text="Condition:")
        self.label_condition.grid(row=2, column=0, sticky="e")
        self.label_condition.config(font=("Helvetica", 18))

        conditions = ["After session", "Before session", "Rest day", "Baseline weight"]
        self.dropdown_condition = ttk.Combobox(self.root, values=conditions, textvariable=self.condition_var, state='readonly')
        self.dropdown_condition.grid(row=2, column=1, sticky="w")
        self.dropdown_condition.config(font=("Helvetica", 18))
        self.dropdown_condition.bind("<<ComboboxSelected>>", self.update_water_entry_state)

        # Weight
        self.label_weight = tk.Label(self.root, text="Weight (g):")
        self.label_weight.grid(row=3, column=0, sticky="e")

        self.entry_weight = tk.Entry(self.root, textvariable=self.weight_var)
        self.entry_weight.grid(row=3, column=1, sticky="w")
        self.entry_weight.config(font=("Helvetica", 18))

        # Water collected
        self.label_water = tk.Label(self.root, text="Water collected (mL):")
        self.label_water.grid(row=4, column=0, sticky="e")

        self.entry_water = tk.Entry(self.root, textvariable=self.water_var, state='normal')  # Initially enabled
        self.entry_water.grid(row=4, column=1, sticky="w")
        self.entry_water.config(font=("Helvetica", 18))

        # Plot frame
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.grid(row=0, column=2, rowspan=5, padx=10, pady=10, sticky="nsew")

        # Submit button
        self.submit_button = tk.Button(self.root, text="Submit", command=self.submit_data)
        self.submit_button.grid(row=5, column=1, sticky="ew", pady=(10, 0))

    def load_dataframe(self):
        try:
            # Try to load the existing dataframe from the CSV file
            df = pd.read_csv("water-log_VR.csv")
        except FileNotFoundError:
            # If the file doesn't exist, create an empty dataframe
            df = pd.DataFrame(columns=["date", "mouse_id", "condition", "weight", "water_collected", "suggested_water"])
        return df
    
    def get_current_date(self):
        now = datetime.now()
        date_str = now.strftime("%m-%d-%Y")
        self.date_var.set(date_str)
        
    def update_water_entry_state(self, event):
        # Enable or disable the Water collected entry based on the selected condition
        condition = self.condition_var.get()
        if condition == "After session":
            self.entry_water.config(state='normal')
        else:
            self.entry_water.config(state='disabled')

    def calculate_target_weight(self, mouse_id):
        # Filter the dataframe by the given mouse ID and condition 'Baseline weight'
        baseline_df = self.df[(self.df["mouse_id"] == mouse_id) & (self.df["condition"] == "Baseline weight")]
        print(baseline_df)
        if baseline_df.empty:
            messagebox.showerror("Error", f"No recovered baseline data for mouse {mouse_id}.")
            return None  # No baseline weight data found for the given mouse ID

        # Calculate the average baseline weight
        avg_baseline_weight = baseline_df["weight"].mean()

        # Calculate the Target weight (80% of the average baseline weight)
        target_weight = avg_baseline_weight * 0.8

        return target_weight

    def reset_entry_fields(self):
        # Reset all entry fields to their default values
        self.get_current_date()
        self.mouse_id_var.set("")
        self.condition_var.set("After session")
        self.weight_var.set("")
        self.water_var.set("")
        
    def submit_data(self):
        
        # Get values from the entry widgets
        date = self.date_var.get()
        mouse_id = int(self.mouse_id_var.get())
        condition = self.condition_var.get()
        weight = self.weight_var.get()
        water = self.water_var.get()

        # Check if any of the required fields is empty
        if not all([date, mouse_id, condition, weight]) or (condition == "After session" and not water):
            messagebox.showerror("Error", "Please fill in all the required fields.")
            return  # Do not proceed with submission
        
        # Validate Weight
        if not self.validate_weight():
            messagebox.showerror("Error", "Weight must be a number between 15 and 40.")
            return
        
        # Validate Mouse ID
        if not self.validate_mouse_id():
            messagebox.showerror("Error", "Mouse ID must be a 6-digit number.")
            return

        # Get Mouse ID and filter dataframe
        filtered_df = self.df[self.df["mouse_id"] == mouse_id]
        
        if condition == 'Baseline weight' and filtered_df.empty:
            messagebox.showinfo("Info", f"First time adding weight about Mouse {mouse_id}, createing new entry")
        
        if condition != 'Baseline weight' and filtered_df.empty:
            messagebox.showinfo("Info", f"No data found for Mouse ID {mouse_id}.")
            return
        
        # Calculate suggested water
        suggested_water = 0.0  # Default value if calculation fails
        try:
            # Calculate the suggested water based on the inputted weight and target weight
            if condition != 'Baseline weight':
                target_weight = self.calculate_target_weight(int(self.mouse_id_var.get()))
                if target_weight is not None:
                    inputted_weight = float(self.weight_var.get())
                    suggested_water = max(max(0, 1-float(water)),target_weight - inputted_weight)
        except ValueError:
            pass  # Ignore calculation errors and use the default value

        # Fill the suggested water field
        self.water_var.set(f"{suggested_water:.2f}")
 
         # Create a new DataFrame with the updated data
        new_entry = {
            "date": date,
            "mouse_id": mouse_id,
            "condition": condition,
            "weight": float(weight),
            "water_collected": float(water) if condition == "After session" else None,
            "suggested_water":float(suggested_water) if condition == 'After session' else 'N/A'
        }
        new_df = pd.DataFrame([new_entry])

        # Concatenate the new DataFrame with the existing one
        self.df = pd.concat([self.df, new_df], ignore_index=True)

        # Save the updated dataframe to a CSV file
        self.save_dataframe()

        # Print the dataframe (for demonstration purposes)
        print(self.df)

        # Get Mouse ID and filter dataframe
        filtered_df = self.df[self.df["mouse_id"] == mouse_id]
        
        # Plotting on the existing Axes
        self.ax.clear()
        self.ax.plot(filtered_df["date"], filtered_df["weight"], marker='o', linestyle='-', label="Weight Data")
        if condition != 'Baseline weight':
            self.ax.axhline(y=target_weight, linestyle='--', color='gray', label="Target Weight")

        # Set font size for axis labels, title, and legend
        font_size = 12
        self.ax.set_title(f"Weight Data for Mouse ID {mouse_id}", fontsize=font_size)
        self.ax.set_xlabel("Date", fontsize=font_size)
        self.ax.set_ylabel("Weight (g)", fontsize=font_size)
        self.ax.legend(fontsize=font_size)

        # Update the embedded plot in Tkinter window
        self.plot_canvas.draw()

        # Reset entry fields to default values
        self.reset_entry_fields()
        
        # Display a pop-up with a summary of inputted data
        if condition != 'Baseline weight':
            summary_message = (
                f"Date: {date}\n"
                f"Mouse ID: {mouse_id}\n"
                f"Condition: {condition}\n"
                f"Weight (g): {weight}\n"
                f"Water collected (mL): {water}\n"
                f"Target Weight: {target_weight:.2f}\n"
                f"Suggested Water: {suggested_water:.2f}\n"
            )
            
            messagebox.showinfo("Submission Summary", summary_message)
        
    def validate_weight(self):
        try:
            weight = float(self.weight_var.get())
            if 15 <= weight <= 40:
                return True
            else:
                return False
        except ValueError:
            return False

    def validate_mouse_id(self):
        mouse_id = self.mouse_id_var.get()
        if not mouse_id.isdigit() or len(mouse_id) != 6:
            return False
        return True
    
    def save_dataframe(self):
        # Save the dataframe to a CSV file
        self.df.to_csv("water-log_VR.csv", index=False)

    def plot_data(self):
        # Validate Mouse ID
        if not self.validate_mouse_id():
            messagebox.showerror("Error", "Mouse ID must be a 6-digit number.")
            return

        # Get Mouse ID and filter dataframe
        mouse_id = int(self.mouse_id_var.get())
        filtered_df = self.df[self.df["mouse_id"] == mouse_id]
        filtered_df = self.filtered_df.tail(20)

        if filtered_df.empty:
            messagebox.showinfo("Info", f"No data found for Mouse ID {mouse_id}.")
            return

        # Plotting on the existing Axes
        self.ax.clear()
        
        # Calculate Target weight
        target_weight = self.calculate_target_weight(mouse_id)

        # Retrieve the last 20 entries from the DataFrame

        
        # Plotting on the existing Axes
        self.ax.clear()
        self.ax.plot(filtered_df["date"], filtered_df["weight"], marker='o', linestyle='-', label="Weight Data")
        self.ax.axhline(y=target_weight, linestyle='--', color='gray', label="Target Weight")
        self.ax.set_title(f"Weight Data for Mouse ID {mouse_id}")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Weight (g)")

        # Update the embedded plot in Tkinter window
        self.plot_canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = DataEntryApp(root)
    root.mainloop()
