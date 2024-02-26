import os
import piexif
from PIL import Image, ExifTags


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
    # Take the absolute value since direction determines the sign
    decimal_degree_abs = abs(decimal_degree)
    degrees = int(decimal_degree_abs)
    minutes_float = (decimal_degree_abs - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60

    # Determine cardinal direction based on original value and specified direction
    if direction == 'Latitude':
        cardinal = 'N' if decimal_degree >= 0 else 'S'
    else:  # Longitude
        cardinal = 'E' if decimal_degree >= 0 else 'W'

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

    return lat_readable,lon_readable

def get_image_location(image_path):
    try:
        img = Image.open(image_path)
        exif_dict = piexif.load(img.info.get('exif', {}))  # Use .get to avoid KeyError

        if not exif_dict:
            return None, "No EXIF data found"
        
        gps_info = exif_dict.get('GPS')
        if gps_info:
            coordinates = GPSInfo_to_coordinates(gps_info)
            print(f'GPS coordinates 1111: {coordinates}')
            return coordinates
        else:
            return None, "No GPS data found"
    except Exception as e:
        return None, str(e)  # Return the error message
    
def get_image_exif(image_path):
    img = Image.open(image_path)
    exif_data = img._getexif()

    if not exif_data:
        return "No EXIF data found."

    tags = {ExifTags.TAGS[k]: v for k, v in exif_data.items() if k in ExifTags.TAGS}

    desired_tags = [
        'DateTimeOriginal', 'Make', 'Model', 'LensModel', 'GPSAltitude',
        'Software', 'RunTimeSincePowerUp', 'FocalLength', 'FNumber', 'ExposureTime',
        'ISOSpeedRatings', 'ExposureBiasValue', 'ExposureProgram', 'MeteringMode',
        'Flash', 'FocalLengthIn35mmFilm', 'SceneCaptureType', 'Contrast', 'Saturation',
        'Sharpness', 'SubjectDistanceRange', 'ExposureMode', 'WhiteBalance', 'GainControl',
        'LightSource', 'SensingMethod', 'ExposureIndex', 'FileSource', 'SceneType',
        'CustomRendered', 'DigitalZoomRatio'
    ]

    found_data = False  # Flag to track if any data is found
    exif_str = ""
    for tag in desired_tags:
        if tag in tags:
            exif_str += f"{tag}: {tags[tag]}\n"
            found_data = True

    if not found_data:
        return "No EXIF data found for the desired tags."
    else:
        exif_str += "No other data was found."  # This line can be adjusted based on what you want to convey

    return exif_str