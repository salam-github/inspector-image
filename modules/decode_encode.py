from PIL import Image
import os



def unique_file_path(base_path):
    """Generates a unique file path by appending an incrementing number if the file already exists."""
    counter = 1  # Start counter at 1
    directory, filename = os.path.split(base_path)
    name, ext = os.path.splitext(filename)
    
    # Start with the original filename (without a number)
    unique_path = base_path
    # Append "_1", "_2", etc., if the file exists
    while os.path.exists(unique_path):
        unique_path = os.path.join(directory, f"{name}_{counter}{ext}")
        counter += 1
    
    return unique_path

def encode_message(image_path, message, output_image_path=None):
    intermediate_image_path = None
    original_ext = os.path.splitext(image_path)[1].lower()
    
    if original_ext in ['.jpeg', '.jpg']:
        intermediate_image_path = image_path.rsplit('.', 1)[0] + '.png'
        img = Image.open(image_path)
        img.save(intermediate_image_path, 'PNG')
        image_to_encode = intermediate_image_path
    else:
        image_to_encode = image_path

    img = Image.open(image_to_encode)
    encoded = img.copy()
    width, height = img.size
    delimiter = "~~~"
    message = delimiter + message + delimiter
    message_binary = ''.join(format(ord(char), '08b') for char in message)
    
    if output_image_path is None:
        directory, filename = os.path.split(image_to_encode)
        name = os.path.splitext(filename)[0]
        output_image_path = os.path.join(directory, f"encoded_{name}.png")
    
    # Generate a unique file path to avoid overwriting existing files
    output_image_path = unique_file_path(output_image_path)

    idx = 0
    for row in range(height):
        for col in range(width):
            if idx < len(message_binary):
                pixel = list(img.getpixel((col, row)))
                for i in range(3):
                    if idx < len(message_binary):
                        pixel[i] = pixel[i] & ~1 | int(message_binary[idx])
                        idx += 1
                encoded.putpixel((col, row), tuple(pixel))
            else:
                encoded.save(output_image_path)
                if intermediate_image_path:
                    os.remove(intermediate_image_path)
                return f"Message encoded successfully. Output image saved to {output_image_path}"
    
    if intermediate_image_path:
        os.remove(intermediate_image_path)
    return "Failed to encode the entire message."
    
    # Delete the intermediate PNG if no message was fully encoded
    if intermediate_image_path:
        os.remove(intermediate_image_path)
    return "Failed to encode the entire message."

def decode_message(image_path):
    img = Image.open(image_path)
    width, height = img.size
    binary_message = ""
    
    for row in range(height):
        for col in range(width):
            pixel = img.getpixel((col, row))
            for i in range(3):  # Modify this line to iterate over RGB components
                binary_message += str(pixel[i] & 1)
    
    bits = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
    message = "".join([chr(int(bit, 2)) for bit in bits])
    
    delimiter = "~~~"
    if delimiter in message:
        start = message.find(delimiter) + len(delimiter)
        end = message.rfind(delimiter)
        return message[start:end]
    return "No hidden message found."