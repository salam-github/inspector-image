import tkinter as tk
import requests
from io import BytesIO
import re
import os
from tkinter import filedialog, messagebox, Text, Scrollbar
from PIL import Image, ImageTk
import tkinter.simpledialog as simpledialog
import configparser
from pathlib import Path
from decode_encode import encode_message, decode_message
from shared import get_image_location, extract_pgp_key, get_decimal_from_dms  # Ensure correct import paths

class ImageInspectorApp:
    def __init__(self, root):
        super().__init__()
        self.api_key = ""
        self.load_api_key()
        self.root = root
        self.root.title("Image Inspector Tool")

        # Setup frames
        self.left_frame = tk.Frame(self.root, width=200, height=400)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.right_frame = tk.Frame(self.root, width=400, height=400)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.minsize(800, 400)

        # Setup widgets
        self.setup_widgets()

    def setup_widgets(self):
        # Image path entry
        tk.Label(self.left_frame, text="Image Path:").pack(anchor='nw')
        self.entry_image_path = tk.Entry(self.left_frame, width=50)
        self.entry_image_path.pack(anchor='nw')
        tk.Button(self.left_frame, text="Select Image", command=self.select_image).pack(anchor='nw')

        # Message entry
        # tk.Label(self.left_frame, text="Message:").pack(anchor='nw')
        # self.entry_message = tk.Entry(self.left_frame, width=50)
        # self.entry_message.pack(anchor='nw')

        # Operation buttons
        tk.Button(self.left_frame, text="Encode Message", command=self.encode).pack(anchor='nw')
        tk.Button(self.left_frame, text="Decode Message", command=self.decode).pack(anchor='nw')
        tk.Button(self.left_frame, text="Extract GPS Location", command=self.extract_gps).pack(anchor='nw')
        tk.Button(self.left_frame, text="Extract PGP Key", command=self.extract_pgp).pack(anchor='nw')

        # Output Text Widget
        self.output_text = Text(self.right_frame, wrap="word")
        self.output_text.pack(expand=True, fill='both')

        # Scrollbar for Text Widget
        scrollbar = Scrollbar(self.output_text, command=self.output_text.yview)
        self.output_text['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side='right', fill='y')
    
    def load_api_key(self):
        config = configparser.ConfigParser()
        # Construct the path to the configuration file
        config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config1.ini')
        config.read(config_file_path)
        self.api_key = config['Geoapify']['api_key']

    def select_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
         self.clear_gui_elements()  # Clear the output and map if they exist
         self.entry_image_path.delete(0, tk.END)
         self.entry_image_path.insert(0, file_path)

         self.display_image(file_path)  # Call display_image to show the image

    def display_image(self, file_path):
        img = Image.open(file_path)
        img.thumbnail((200, 200))  # Adjust size as needed
        img_tk = ImageTk.PhotoImage(img)

        if hasattr(self, 'image_preview_label'):
            self.image_preview_label.configure(image=img_tk)
        else:
            self.image_preview_label = tk.Label(self.left_frame, image=img_tk)
            self.image_preview_label.pack()

        # Keep a reference to the new image to prevent garbage-collection
        self.image_preview_label.image = img_tk

    def encode(self):
        image_path = self.entry_image_path.get()
        if image_path:
         # Prompt for the message using a dialog
            message = simpledialog.askstring("Encode Message", "Enter the message to encode:")
            if message:
                result = encode_message(image_path, message)  # Proceed with encoding
                self.output_text.delete('1.0', tk.END)  # Clear existing output
                self.output_text.insert(tk.END, "Encode Result:\n" + result)
            else:
             messagebox.showinfo("Encode Message", "Encoding cancelled or no message entered.")
        else:
            messagebox.showerror("Error", "Image path is required.")

    def decode(self):
        image_path = self.entry_image_path.get()
        if image_path:
            self.clear_map_display()  # Clear the map if it exists
            message = decode_message(image_path)  # Adjusted to class method call
            self.output_text.delete('1.0', tk.END)  # Clear existing output
            self.output_text.insert(tk.END, "Decoded Message:\n" + message)
        else:
            messagebox.showerror("Error", "Image path is required.")

    def parse_dms_to_tuple(self, dms_str):
        # Extract degrees, minutes, seconds, and direction from the DMS string
        match = re.match(r"(\d+)° (\d+)' ([\d.]+)\" ([NSEW])", dms_str)
        if match:
            degrees, minutes, seconds, direction = match.groups()
         # Convert degrees, minutes, and seconds to numeric values
            dms_tuple = ((int(degrees), 1), (int(minutes), 1), (float(seconds), 1))
            return dms_tuple, direction
        return None, None

    
    def extract_gps(self):
        image_path = self.entry_image_path.get()
        if image_path:
            location_str = get_image_location(image_path)
            if location_str:
                # Extract numeric values and direction reference from DMS strings
                lat_str, lon_str = location_str
                lat_dms, lat_ref = self.parse_dms_to_tuple(lat_str)
                lon_dms, lon_ref = self.parse_dms_to_tuple(lon_str)

                # Convert DMS to decimal degrees using the shared function
                lat_decimal = get_decimal_from_dms(lat_dms, lat_ref)
                lon_decimal = get_decimal_from_dms(lon_dms, lon_ref)

                if lat_decimal is not None and lon_decimal is not None:
                    self.show_map(lat_decimal, lon_decimal)
                    
                else:
                    messagebox.showinfo("GPS Location", "Invalid GPS data format.", message="Invalid GPS data format.")
            else:
                messagebox.showinfo("GPS Location", "No GPS data found.")
        else:
            messagebox.showerror("Error", "Image path is required.")
        
    def show_map(self, lat, lon):
        api_key = self.api_key  # Replace with your actual Geoapify API key
        # Construct the request URL for Geoapify Static Maps API
        url = f"https://maps.geoapify.com/v1/staticmap?style=osm-bright-smooth&width=400&height=400&center=lonlat:{lon},{lat}&zoom=10&marker=lonlat:{lon},{lat};type:awesome;color:%23ff0000;size:medium&apiKey={api_key}"
    
        try:
            response = requests.get(url)
            if response.status_code == 200:
             # Convert the response content into an image
                image_data = BytesIO(response.content)
                img = Image.open(image_data)
                img_tk = ImageTk.PhotoImage(img)
            
                # Display the image in the Tkinter window
                if hasattr(self, 'map_label') and self.map_label.winfo_exists():
                    self.map_label.configure(image=img_tk)
                    self.map_label.image = img_tk  # Keep a reference to prevent garbage-collection
                else:
                    self.map_label = tk.Label(self.right_frame, image=img_tk)
                    self.map_label.pack()
                    self.output_text.insert(tk.END, f"Latitude: {lat}\nLongitude: {lon}\n")

                self.map_label.image = img_tk  # Keep a reference to prevent garbage-collection
            else:
                messagebox.showerror("Error", "Failed to retrieve the map image.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display map: {e}")


    def extract_pgp(self):
        image_path = self.entry_image_path.get()
        if image_path:
            self.clear_map_display()  # Clear the map if it exists
            pgp_key = extract_pgp_key(image_path)  # Adjusted to class method call
            self.output_text.delete('1.0', tk.END)  # Clear existing output
            self.output_text.insert(tk.END, "PGP Key:\n" + pgp_key)
        else:
            messagebox.showerror("Error", "Image path is required.")

    def clear_gui_elements(self):
        # Clear output text where PGP keys, maps, or messages are displayed
        self.output_text.delete('1.0', tk.END)
    
        # Remove the map image if it exists
        if hasattr(self, 'map_label') and self.map_label.winfo_exists():
            self.map_label.destroy()

    def clear_map_display(self):
     # Check if the map_label exists and is displayed, then hide or destroy it
        if hasattr(self, 'map_label') and self.map_label.winfo_exists():
            self.map_label.destroy()  # Or, self.map_label.pack_forget() to hide without destroying
            del self.map_label  # Remove the attribute reference if destroyed

# Initialize and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageInspectorApp(root)
    root.mainloop()
