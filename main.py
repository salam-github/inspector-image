import argparse
from PIL import Image
from stegano import lsb
import piexif

def print_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
        print(f"Dimensions: {width} x {height}")


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

    parser.add_argument("-dim", action="store_true", help="Print image dimensions")
    parser.add_argument("image", help="Path to the image file")
    parser.add_argument("-map", action="store_true", help="Extract location data from image")
    parser.add_argument("-steg", action="store_true", help="Extract hidden PGP key from image")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.map:
        location = get_image_location(args.image)
        print(f"Lat/Lon: {location}")
    elif args.steg:
        pgp_key = extract_pgp_key(args.image)
        print(pgp_key)

    elif args.dim:
        print_image_dimensions(args.image)

    else:
        print("No valid operation specified. Use -map for location or -steg for PGP key extraction.")

if __name__ == "__main__":
    main()
