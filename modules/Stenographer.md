# Image Steganography Tool

This tool is designed to embed hidden messages within images, with a focus on preserving the integrity of the message across different image formats. This README details the encoding and decoding processes, addresses challenges encountered, particularly with JPEG images, and explains the solutions implemented.

## Encoding Process

The encoding process involves several steps to embed a message into an image. For JPEG images, an initial conversion to PNG is performed to avoid issues with lossy compression.

### Step 1: Image Conversion for JPEGs

JPEG images are converted to PNG to ensure lossless data preservation:

```python
if original_ext in ['.jpeg', '.jpg']:
    intermediate_image_path = image_path.rsplit('.', 1)[0] + '.png'
    img = Image.open(image_path)
    img.save(intermediate_image_path, 'PNG')
    image_to_encode = intermediate_image_path
```

### Step 2: Message Preparation

The message is framed with delimiters to mark its boundaries:

```python
delimiter = "~~~"
message = delimiter + message + delimiter
```

### Step 3: Binary Encoding

The message is converted into a binary representation:

```python
message_binary = ''.join(format(ord(char), '08b') for char in message)
```

### Step 4: Pixel Modification

The least significant bit of each color component in the image pixels is modified:

```python
for row in range(height):
    for col in range(width):
        if idx < len(message_binary):
            pixel = list(img.getpixel((col, row)))
            for i in range(3):
                if idx < len(message_binary):
                    pixel[i] = pixel[i] & ~1 | int(message_binary[idx])
                    idx += 1
            encoded.putpixel((col, row), tuple(pixel))
```

### Step 5: Unique File Saving

The modified image is saved with a unique filename to avoid overwriting:

```python
output_image_path = unique_file_path(output_image_path)
encoded.save(output_image_path)
```

### Step 6: Cleanup

Intermediate PNG files created from JPEGs are deleted:

```python
if intermediate_image_path:
    os.remove(intermediate_image_path)
```

## Decoding Process

To extract a hidden message, the tool reverses the encoding process:

```python
img = Image.open(image_path)
binary_message = ""
for row in range(height):
    for col in range(width):
        pixel = img.getpixel((col, row))
        for i in range(3):
            binary_message += str(pixel[i] & 1)
```

The binary data is then converted back to text, extracting the message between the delimiters:

```python
bits = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]
message = "".join([chr(int(bit, 2)) for bit in bits])
if "~~~" in message:
    start = message.find("~~~") + 3
    end = message.rfind("~~~")
    hidden_message = message[start:end]
```

## Challenges with JPEG Compression

JPEG's lossy compression posed a challenge for steganography, as it could alter or discard the LSB modifications used to embed messages. To overcome this, JPEG images are first converted to PNG, a lossless format, ensuring the embedded message remains intact.

## Conclusion

This steganography tool offers a straightforward method for embedding and extracting hidden messages within images. By addressing the challenges associated with JPEG compression through image conversion, it ensures reliable message preservation and recovery.

