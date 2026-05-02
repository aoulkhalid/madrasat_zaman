from detection_of_hides import detect_and_save_circles


import os

FOLDER = "/home/mohamed/Documents/mohamed/madrasat_zaman/assets/images/diff"

solution_files = []

for root, dirs, files in os.walk(FOLDER):
    for file in files:
        if "solution" in file.lower():  # case-insensitive match
            full_path = os.path.join(root, file)
            solution_files.append(full_path)

print("Found files:")
for path in solution_files:
    print(path)
    detect_and_save_circles(path, "my_output.txt")      # custom path


print("\nTotal:", len(solution_files))