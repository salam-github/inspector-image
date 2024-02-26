# Image Inspector Tool

The Image Inspector tool is a versatile Python application designed for steganography and metadata extraction from images. It allows users to encode hidden messages into images, decode messages from images, extract PGP keys hidden within images, dump relevant exif data and retrieve the geographical location where the photo was taken based on its metadata.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Dependencies](#dependencies)
- [Setup](#setup)
- [Usage](#usage)
  - [Encoding a Message](#encoding-a-message)
  - [Decoding a Message](#decoding-a-message)
  - [Extracting PGP Key](#extracting-pgp-key)
  - [Extracting Geolocation Data](#extracting-geolocation-data)
  - [Extracting EXIF Data](#extracting-other-exif-data)
- [GUI Interface](#gui-interface)
  - [Obtaining a Geoapify API Key](#obtaining-a-geoapify-api-key)
  - [Configuring the Application](#configuring-the-application)
  - [Running the GUI](#running-the-gui)
- [Disclaimer](#disclaimer)
- [Challenges and Solutions](#challenges-and-solutions)
- [Contribution](#contribution)
- [License](#license)
- [Detailed Encoding/Decoding Process](#detailed-encodingdecoding-process)

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

Replace `image.png` with the path to your target image.

### Encoding a Message

Encode a hidden message into an image. If the source image is in JPEG format, it will be automatically converted to PNG to ensure lossless data preservation during the encoding process. The output will be a PNG file, even if the input is JPEG.

```sh
python main.py -encode -message "Your secret message" resources/image.jpeg
```

**Note:** Due to the automatic conversion of JPEG images to PNG for encoding, remember to use the `.png` extension for the encoded file when attempting to decode or perform any further operations.

### Decoding a Message

Decode the hidden message from an encoded image. Ensure you refer to the PNG file created during the encoding process, as JPEG inputs are converted to PNG for lossless data preservation.

```sh
python main.py -decode resources/encoded_image.png
```

### Extracting PGP Key

```sh
python main.py -steg resources/image.jpeg
```

### Extracting Geolocation Data

```sh
python main.py -map resources/image.jpeg
```

### Extracting other EXIF Data
```sh
python main.py -exif resources/image.jpeg
```

## GUI Interface

The Image Inspector tool also features a graphical user interface (GUI) to provide an interactive and user-friendly way to utilize its functionalities. The GUI supports all core features, including encoding and decoding messages, extracting PGP keys, and displaying geolocation data on a map.

### Obtaining a Geoapify API Key

To use the geolocation extraction feature and display maps within the GUI, you need a Geoapify API key. Follow these steps to obtain a free API key:

1. Visit [Geoapify](https://www.geoapify.com/) and sign up for an account.
2. Once logged in, navigate to your Dashboard and create a new API key.
3. Choose a plan that suits your needs. The free tier should be sufficient for basic usage and testing.

Remember to keep your API key private and secure.

### Configuring the Application

Before running the GUI or command-line tool, you need to configure your application with your Geoapify API key. This is done by modifying the `config.ini` file located in the root directory of the project:

1. Locate the `config.example.ini` file in the project root.
2. Copy this file and rename the copy to `config.ini`.
3. Open `config.ini` in a text editor and replace `your_api_key_here` with your actual Geoapify API key under the `[Geoapify]` section.

**Note:** The `config.ini` file is ignored by Git to prevent your API key from being accidentally pushed to public repositories. Always ensure that your API key is kept secure and not disclosed in shared or public spaces.

## Running the GUI

To launch the graphical user interface, navigate to the project directory in your terminal and run the following command:

```sh
python modules/gui.py
```
The GUI window will open, allowing you to access all the functionalities of the Image Inspector tool interactively. Ensure you have configured the config.ini file with your Geoapify API key to use the geolocation feature.

## Disclaimer

This tool is provided for educational and research purposes only. The use of the Image Inspector tool for embedding or extracting data in images should be done with the owner's consent and in compliance with all applicable laws and regulations.

## Challenges and Solutions

During the development, we encountered challenges with JPEG images due to their lossy compression, which could potentially alter or remove the hidden data. To address this, the tool automatically converts JPEG images to PNG format before encoding the message. This ensures the integrity of the hidden data, leveraging PNG's lossless compression. While this adds a step in processing JPEG images, it significantly enhances the tool's reliability and broadens its applicability across different image formats.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Detailed Encoding/Decoding Process

For an in-depth explanation of the encoding and decoding processes, including challenges with JPEG compression and our solutions, please refer to our [Detailed Encoding/Decoding README](modules/Stenographer.md).
