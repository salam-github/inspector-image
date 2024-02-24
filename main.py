import argparse
from PIL import Image
import piexif
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
        

def get_decimal_from_dms(dms, ref):
    """
    Convert GPS coordinates in degrees, minutes, and seconds format
    into decimal degrees format, considering the hemisphere reference.
    Each part of DMS is a tuple (numerator, denominator).
    """
    degrees, minutes, seconds = [x[0] / x[1] for x in dms]  # Convert each part of DMS from fraction to decimal
    
    decimal_degrees = degrees + minutes / 60.0 + seconds / 3600.0
    
    # Apply the hemisphere reference to adjust the sign
    if ref in ['S', 'W']:
        decimal_degrees *= -1
    
    return decimal_degrees

def decimal_to_dms(decimal_degree, direction):
    degrees = int(decimal_degree)
    minutes_float = (decimal_degree - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60

    cardinal = 'N' if direction == 'Latitude' else 'E'
    if degrees < 0:
        cardinal = 'S' if direction == 'Latitude' else 'W'
        degrees = degrees * -1  # Make positive for formatting

    return f"{degrees}° {minutes}' {seconds:.2f}\" {cardinal}"

def GPSInfo_to_coordinates(gps_info):
    lat_ref = gps_info[piexif.GPSIFD.GPSLatitudeRef].decode('utf-8')
    lon_ref = gps_info[piexif.GPSIFD.GPSLongitudeRef].decode('utf-8')

    lat = gps_info[piexif.GPSIFD.GPSLatitude]
    lon = gps_info[piexif.GPSIFD.GPSLongitude]

    lat_decimal = get_decimal_from_dms(lat, lat_ref)
    lon_decimal = get_decimal_from_dms(lon, lon_ref)
    
    # Convert decimal degrees to human-readable format (DMS with cardinal direction)
    lat_readable = decimal_to_dms(lat_decimal, 'Latitude')
    lon_readable = decimal_to_dms(lon_decimal, 'Longitude')

    return f"Latitude: {lat_readable}\nLongitude: {lon_readable}"

def get_image_location(image_path):
    img = Image.open(image_path)
    exif_dict = piexif.load(img.info['exif'])

    if not exif_dict:
        return "No EXIF data found"
    
    gps_info = exif_dict.get('GPS')
    if gps_info:
        coordinates = GPSInfo_to_coordinates(gps_info)
        return coordinates
    else:
        return "No GPS data found"



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
        if args.map:
            location = get_image_location(args.image)
            print(location)
    
        if args.steg:
          pgp_key = extract_pgp_key(args.image)
          print(pgp_key)

        if args.decode:  
            message = decode_message(args.image)
            print(f"Hidden message: {message}")

        if args.encode:
            message = args.message
            encode_message_result = encode_message(args.image, message)
            print(encode_message_result)

        # If no operation was specified
        if not (args.map or args.steg or args.decode or args.encode):
            print("No valid operation specified. Use -map, -steg, -decode, or -encode.")

if __name__ == "__main__":
    main()
