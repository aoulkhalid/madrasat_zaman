from test import get_solution_position
import os
import re

FOLDER = "/home/mohamed/Documents/mohamed/madrasat_zaman/assets/images/diff/differences"

solution_files = []

# collect files
for root, dirs, files in os.walk(FOLDER):
    for file in files:
        if "solution" in file.lower():
            full_path = os.path.join(root, file)
            solution_files.append(full_path)

# 🔥 sort numerically (important)
def extract_number(path):
    name = os.path.basename(path)
    match = re.search(r"\d+", name)
    return int(match.group()) if match else float("inf")

solution_files = sorted(solution_files, key=extract_number)

# print files correctly
print(len(solution_files))
for s in solution_files:
    print(s)

# process files with index
i = 1
for path in solution_files:
    get_solution_position(path, i)
    i += 1

print("\nTotal:", len(solution_files))