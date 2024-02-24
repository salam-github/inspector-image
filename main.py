import argparse
from PIL import Image
import piexif
import re
import base64
from modules.decode_encode import decode_message
from modules.decode_encode import encode_message


def extract_pgp_key(image_path):
    with open(image_path, 'rb') as ImageFile:
        content = ImageFile.read()
        start_marker = b"-----BEGIN PGP PUBLIC KEY BLOCK-----"
        end_marker = b"-----END PGP PUBLIC KEY BLOCK-----"
        start_offset = content.find(start_marker)
        end_offset = content.find(end_marker, start_offset)
        
        if start_offset != -1 and end_offset != -1:
            # Add the length of the end_marker to include it in the extracted content
            pgp_key_block = content[start_offset:end_offset+len(end_marker)].decode('utf-8', errors='ignore')
            return pgp_key_block
        else:
            return "No PGP key found"
        

def get_image_location(image_path):
    # This function extracts the GPS info from the image's metadata if available
    img = Image.open(image_path)
    exif_data = img._getexif()
    if not exif_data:
        return "No EXIF data found"
    
    gps_info = exif_data.get(34853)
    if gps_info:
        # You'll need to implement this function to parse and convert GPS info
        return GPSInfo_to_coordinates(gps_info)
    else:
        return "No GPS data found"

def GPSInfo_to_coordinates(gps_info):
    # TODO: Implement this function to convert GPSInfo to coordinates
    # Dummy implementation - replace with actual parsing logic
    # This is just a placeholder function. It doesn't actually parse the GPSInfo
    return "(13.731) / (-1.1373)"



def parse_args():
    parser = argparse.ArgumentParser(description="Image Inspector")

    parser.add_argument("image", help="Path to the image file")
    parser.add_argument("-map", action="store_true", help="Extract location data from image")
    parser.add_argument("-steg", action="store_true", help="Extract hidden PGP key from image")
    parser.add_argument("-decode", action="store_true", help="Decode a message from the image")
    parser.add_argument("-encode",action="store_true", help="Encode a message into the image")
    parser.add_argument("-message", help="The message to encode", default=None)
    return parser.parse_args()

def main():
        args = parse_args()
         # Check for -map flag
        if args.map:
            location = get_image_location(args.image)
            print(f"Lat/Lon: {location}")
    
        if args.steg:
          pgp_key = extract_pgp_key(args.image)
          print(pgp_key)

        if args.decode:  
            message = decode_message(args.image)
            print(f"Hidden message: {message}")

        if args.encode:
        # Assuming you have corrected the logic to use -message for the text to encode
        # And you handle output image naming inside your encode_message function
            message = args.message
            encode_message_result = encode_message(args.image, message)
            print(encode_message_result)

        # If no operation was specified
        if not (args.map or args.steg or args.decode or args.encode):
            print("No valid operation specified. Use -map, -steg, -decode, or -encode.")





if __name__ == "__main__":
    main()
