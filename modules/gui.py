import tkinter as tk
import requests
from io import BytesIO
import webbrowser
from tkinter import filedialog, messagebox, Text, Scrollbar
from PIL import Image, ImageTk
from decode_encode import encode_message, decode_message
from shared import get_image_location, extract_pgp_key  # Ensure correct import paths

class ImageInspectorApp:
    def __init__(self, root):
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
        tk.Label(self.left_frame, text="Message:").pack(anchor='nw')
        self.entry_message = tk.Entry(self.left_frame, width=50)
        self.entry_message.pack(anchor='nw')

        # Operation buttons
        tk.Button(self.left_frame, text="Encode Message", command=self.encode).pack(anchor='nw')
        tk.Button(self.left_frame, text="Decode Message", command=self.decode).pack(anchor='nw')
        tk.Button(self.left_frame, text="Extract GPS Location", command=self.extract_gps).pack(anchor='nw')
        #tk.Button(self.left_frame, text="Extract PGP Key", command=self.extract_pgp).pack(anchor='nw')

        # Output Text Widget
        self.output_text = Text(self.right_frame, wrap="word")
        self.output_text.pack(expand=True, fill='both')

        # Scrollbar for Text Widget
        scrollbar = Scrollbar(self.output_text, command=self.output_text.yview)
        self.output_text['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side='right', fill='y')
    
    

    def select_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
         self.entry_image_path.delete(0, tk.END)
         self.entry_image_path.insert(0, file_path)
         self.display_image(file_path)  # Call display_image to show the image

    def display_image(self, file_path):
        img = Image.open(file_path)
        img.thumbnail((400, 400))  # Adjust size as needed
        img = ImageTk.PhotoImage(img)

        if hasattr(self, 'image_label'):
            self.image_label.configure(image=img)  # Update existing label
        else:
            self.image_label = tk.Label(self.left_frame, image=img)  # Create new label if it doesn't exist
            self.image_label.pack()

            self.image_label.image = img  # Keep a reference

    def encode(self):
        image_path = self.entry_image_path.get()
        message = self.entry_message.get()
        if image_path and message:
            result = encode_message(image_path, message)  # Adjusted to class method call
            self.output_text.delete('1.0', tk.END)  # Clear existing output
            self.output_text.insert(tk.END, "Encode Result:\n" + result)
        else:
            messagebox.showerror("Error", "Image path and message are required.")

    def decode(self):
        image_path = self.entry_image_path.get()
        if image_path:
            message = decode_message(image_path)  # Adjusted to class method call
            self.output_text.delete('1.0', tk.END)  # Clear existing output
            self.output_text.insert(tk.END, "Decoded Message:\n" + message)
        else:
            messagebox.showerror("Error", "Image path is required.")

    def extract_gps(self):
        image_path = self.entry_image_path.get()
        if image_path:
            location = get_image_location(image_path)
            if location:
                lat, lon = location  # Assuming get_image_location returns a tuple (lat, lon)
                self.show_map(lat, lon)
            else:
                messagebox.showinfo("GPS Location", "No GPS data found or invalid location.")
        else:
            messagebox.showerror("Error", "Image path is required.")

    def get_static_map_image(self, lat, lon):
        # Construct the request URL
        url = f"https://nominatim.openstreetmap.org/search?q={lat},{lon}&format=json"
    
        # Make the request
        response = requests.get(url, headers={"User-Agent": "mozilla/5.0"})
        if response.status_code == 200:
            # Convert the response content into an image
            image_data = BytesIO(response.content)
            img = Image.open(image_data)
            return ImageTk.PhotoImage(img)
        else:
            return None
        
    def show_map(self, lat, lon):
        img = self.get_static_map_image(lat, lon)
        if img:
            if hasattr(self, 'map_label'):
                self.map_label.configure(image=img)
            else:
                self.map_label = tk.Label(self.right_frame, image=img)
                self.map_label.image = img  # Keep a reference!
                self.map_label.pack()
        else:
            messagebox.showerror("Error", "Could not retrieve map image.")

    def extract_pgp(self):
        image_path = self.entry_image_path.get()
        if image_path:
            pgp_key = extract_pgp_key(image_path)  # Adjusted to class method call
            self.output_text.delete('1.0', tk.END)  # Clear existing output
            self.output_text.insert(tk.END, "PGP Key:\n" + pgp_key)
        else:
            messagebox.showerror("Error", "Image path is required.")

# Initialize and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageInspectorApp(root)
    root.mainloop()
