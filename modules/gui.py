import tkinter as tk
import requests
from io import BytesIO
import re
import os
from tkinter import filedialog, messagebox, Text, Scrollbar
from PIL import Image, ImageTk, ImageOps
import tkinter.simpledialog as simpledialog
import configparser
# from pathlib import Path
from decode_encode import encode_message, decode_message
from shared import get_image_location, extract_pgp_key, get_decimal_from_dms, get_image_exif 

class ImageInspectorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Inspector Tool")
        self.api_key = ""
        self.zoom_level = ""
        self.load_api_key_and_zoom()
        self.minsize(200, 600)

        # Setup frames
        self.left_frame = tk.Frame(self, width=200, height=400)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.center_frame = tk.Frame(self, width=200, height=400)  # Center frame for buttons
        self.center_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ns")

        self.right_frame = tk.Frame(self, width=200, height=400)
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=3)
        

        # Setup widgets
        self.setup_widgets()

    def setup_widgets(self):
        # Image path entry
        tk.Label(self.left_frame, text="Image Path:").pack(anchor='nw')
        self.entry_image_path = tk.Entry(self.left_frame, width=20)
        self.entry_image_path.pack(anchor='nw')
        tk.Button(self.left_frame, text="Select Image", command=self.select_image).pack(anchor='nw', pady=(0, 20))

        # Operation buttons now in the center frame
        tk.Button(self.center_frame, text="Encode Message", command=self.encode).pack(anchor='center', pady=5)
        tk.Button(self.center_frame, text="Decode Message", command=self.decode).pack(anchor='center', pady=5)
        tk.Button(self.center_frame, text="Extract GPS Location", command=self.extract_gps).pack(anchor='center', pady=5)
        tk.Button(self.center_frame, text="Extract PGP Key", command=self.extract_pgp).pack(anchor='center', pady=5)
        tk.Button(self.center_frame, text="Show EXIF Data", command=self.show_exif_data).pack(anchor='center', pady=5)

        # Output Text Widget in the right frame
        self.text_frame = tk.Frame(self.right_frame)
        self.text_frame.pack(fill="both", expand=True)

        self.output_text = Text(self.text_frame, wrap="word")
        self.output_text.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(self.text_frame, command=self.output_text.yview)
        scrollbar.pack(side="right", fill="y")

        self.output_text.config(yscrollcommand=scrollbar.set)
    
    def load_api_key_and_zoom(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
        self.api_key = config['Geoapify']['api_key']
        self.zoom_level = config['Geoapify'].get('zoom_level', '12')  # Default to zoom level 15 if not specified


    def select_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
         self.clear_gui_elements()  # Clear the output and map if they exist
         self.entry_image_path.delete(0, tk.END)
         self.entry_image_path.insert(0, file_path)

         self.display_image(file_path)  # Call display_image to show the image

    def correct_image_orientation(self, img):
        try:
            exif = img.getexif()
            orientation_key = 274  # Exif tag for orientation
            if exif and orientation_key in exif:
                orientation = exif[orientation_key]
                rotated_img = ImageOps.exif_transpose(img)
                return rotated_img
        except Exception as e:
            print(f"Failed to correct image orientation: {e}")
        return img

    def display_image(self, file_path):
        img = Image.open(file_path)
        img = self.correct_image_orientation(img)  # Correct the image orientation
        img.thumbnail((300, 300))  # Adjust size as needed
        img_tk = ImageTk.PhotoImage(img)

        if hasattr(self, 'image_preview_label'):
            self.image_preview_label.configure(image=img_tk)
        else:
            self.image_preview_label = tk.Label(self.left_frame, image=img_tk)
            self.image_preview_label.image = img_tk  # Keep a reference
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
        # Ignore negative signs for minutes and seconds by using the absolute value
        match = re.match(r"(\d+)° (\d+)' ([\d.]+)\" ([NSEW])", dms_str)
        if match:
            degrees, minutes, seconds, direction = match.groups()
            # Use absolute values for minutes and seconds to ensure positivity
            dms_tuple = ((int(degrees), 1), (abs(int(minutes)), 1), (abs(float(seconds)), 1))
            print(f"Parsed DMS tuple: {dms_tuple}, Direction: {direction}")
            return dms_tuple, direction
        else:
            print(f"Failed to parse DMS string: {dms_str}")
        return None, None

    
    def extract_gps(self):
        image_path = self.entry_image_path.get()
        if image_path:
            self.clear_gui_elements()  # Clear the output and map if they exist
            location_str = get_image_location(image_path)
            print(f"Extracted GPS string: {location_str}")  # Debug print
            if location_str:
                # Extract numeric values and direction reference from DMS strings
                lat_str, lon_str = location_str
                lat_dms, lat_ref = self.parse_dms_to_tuple(lat_str)
                lon_dms, lon_ref = self.parse_dms_to_tuple(lon_str)
                print(f"lat_dms: {lat_dms}, lon_dms: {lon_dms}")  # Debug print
                print(f"lat_ref: {lat_ref}, lon_ref: {lon_ref}")  # Debug print

                # Convert DMS to decimal degrees using the shared function
                lat_decimal = get_decimal_from_dms(lat_dms, lat_ref)
                lon_decimal = get_decimal_from_dms(lon_dms, lon_ref)
                print(f"lat_decimal: {lat_decimal}, lon_decimal: {lon_decimal}")  # Debug print

                if lat_decimal is not None and lon_decimal is not None:
                    self.show_map(lat_decimal, lon_decimal)
                    
                else:
                    messagebox.showinfo("GPS Location", "Invalid GPS data format.", message="Invalid GPS data format.")
            else:
                messagebox.showinfo("GPS Location", "No GPS data found.")
        else:
            messagebox.showerror("Error", "Image path is required.")
        
    def show_map(self, lat, lon):
        api_key = self.api_key  # Replace with your actual Geoapify API key in the config.ini file
        zoom_level = self.zoom_level  # Replace with your desired zoom level in the config.ini file
        # Construct the request URL for Geoapify Static Maps API
        url = f"https://maps.geoapify.com/v1/staticmap?style=osm-liberty&width=400&height=400&center=lonlat:{lon},{lat}&zoom={zoom_level}&marker=lonlat:{lon},{lat};type:awesome&scaleFactor=1&apiKey={api_key}"
    
        try:
            response = requests.get(url)
            if response.status_code == 200:
             # Convert the response content into an image
                image_data = BytesIO(response.content)
                img = Image.open(image_data)
                img_tk = ImageTk.PhotoImage(img)
            
                # Display the image in the Tkinter window
                if hasattr(self, 'map_label') and self.map_label.winfo_exists():
                    self.clear_gui_elements()  # Clear the output and map if they exist
                    self.map_label.configure(image=img_tk)
                    self.map_label.image = img_tk  # Keep a reference to prevent garbage-collection
                else:
                    self.map_label = tk.Label(self.right_frame, image=img_tk)
                    self.map_label.pack()
                    self.output_text.insert(tk.END, f"Latitude: {lat}\nLongitude: {lon}\n")

                self.map_label.image = img_tk  # Keep a reference to prevent garbage-collection
            else:
                self.output_text.insert(tk.END, f"Latitude: {lat}\nLongitude: {lon}\n")
                messagebox.showerror("Error", "Failed to retrieve the map image. check your API key and internet connection.")
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
            self.map_label.destroy() 
            del self.map_label  # Remove the attribute reference if destroyed

    def show_exif_data(self):
        image_path = self.entry_image_path.get()
        if image_path:
            exif_data = get_image_exif(image_path)
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert(tk.END, exif_data)
        else:
            messagebox.showerror("Error", "Image path is required.")


# Initialize and run the app
if __name__ == "__main__":
    # root = tk.Tk()
    app = ImageInspectorApp()
    app.mainloop()
