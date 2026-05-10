import os
from PIL import Image

INPUT_FOLDER = "/home/mohamed/Documents/mohamed/madrasat_zaman/assets/images/diff"
OUTPUT_FOLDER = "/home/mohamed/Documents/mohamed/madrasat_zaman/assets/images/diff/mohamed/resized_images"

TARGET_SIZE = (640, 480)

# create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# supported formats
VALID_EXT = (".jpeg")

for filename in os.listdir(INPUT_FOLDER):
    if not filename.lower().endswith(VALID_EXT):
        continue

    input_path = os.path.join(INPUT_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    try:
        img = Image.open(input_path)

        # resize to exact 640x480
        img.thumbnail(TARGET_SIZE)
        img_resized = img

        img_resized.save(output_path)

        print(f"Resized: {filename}")

    except Exception as e:
        print(f"Error with {filename}: {e}")