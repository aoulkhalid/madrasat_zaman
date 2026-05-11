import cv2
import numpy as np
import os

def get_solution_position(img_path, img_number):
    img = cv2.imread(img_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filtered = []
    for cnt in contours:
        if cv2.contourArea(cnt) > 100:
            filtered.append(cnt)

    contours = filtered
    centers = []

    # ✅ Get image dimensions
    h, w = img.shape[:2]

    for cnt in contours:
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx_px = M["m10"] / M["m00"]
            cy_px = M["m01"] / M["m00"]

            # ✅ Convert to percentage based on image dimensions
            cx_pct = round((cx_px / w) , 4)
            cy_pct = round((cy_px / h) , 4)

            centers.append((cx_pct, cy_pct, 40))

    img_name = os.path.basename(img_path)

    left = f"{img_number}.Left.jpeg"
    right = f"{img_number}.Right.jpeg"
    title = f"Image {img_number}"

    line = f'{{"left": "{left}",  "right": "{right}",  "title": "{title}", "diffs": {centers}}},\n'

    # ✅ Write to file once (removed duplicate write)
    output_path = os.path.join(os.path.dirname(__file__), "my_output.txt")
    with open(output_path, "a") as f:
        f.write(line)
        print("it been writing into the file !!!!!!!!!!!!!!1")

    return centers