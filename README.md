# Image Inspector Tool

The Image Inspector tool is a versatile Python application designed for steganography and metadata extraction from images. It allows users to encode hidden messages into images, decode messages from images, extract PGP keys hidden within images, and retrieve the geographical location where the photo was taken based on its metadata.

## Features

- **Encode Messages**: Embed secret text messages into images without altering their visual appearance.
- **Decode Messages**: Extract hidden messages from images.
- **Extract PGP Keys**: Retrieve PGP keys embedded within images.
- **Geolocation Extraction**: Determine the geographical location where an image was taken using its EXIF metadata.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.x
- Pip (Python package installer)

## Dependencies

This project requires certain Python libraries to function correctly. These dependencies are listed in a `requirements.txt` file.

To install these dependencies, run the following command in your terminal:

```sh
pip install -r requirements.txt
```

## Setup

To get started with the Image Inspector tool, clone the repository or download the source code to your local machine. Navigate to the project directory, and ensure you have installed all required dependencies as mentioned above.

## Usage

The tool is executed from the command line, with different flags specifying the operation to be performed:

- **Encoding a Message**: 
  ```sh
  python main.py -encode -message "Your secret message" image.png
  ```
- **Decoding a Message**:
  ```sh
  python main.py -decode image.png
  ```
- **Extracting PGP Key**:
  ```sh
  python main.py -steg image.png
  ```
- **Extracting Geolocation Data**:
  ```sh
  python main.py -map image.png
  ```

Replace `image.png` with the path to your target image.

## Disclaimer

This tool is provided for educational and research purposes only. The use of the Image Inspector tool for embedding or extracting data in images should be done with the owner's consent and in compliance with all applicable laws and regulations.

## Challenges and Solutions

During the development, we encountered challenges with JPEG images due to their lossy compression, which could potentially alter or remove the hidden data. To address this, the tool automatically converts JPEG images to PNG format before encoding the message. This ensures the integrity of the hidden data, leveraging PNG's lossless compression. While this adds a step in processing JPEG images, it significantly enhances the tool's reliability and broadens its applicability across different image formats.

## Contribution

Contributions to the Image Inspector tool are welcome. Please feel free to fork the repository, make improvements, and submit pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
