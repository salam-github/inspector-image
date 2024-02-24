import argparse
from modules.decode_encode import decode_message
from modules.decode_encode import encode_message
from modules.shared import get_image_location
from modules.shared import extract_pgp_key



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
            print(f"Lat/Long: {location}")
    
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
