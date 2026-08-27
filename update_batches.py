import re
import os

input_file = "seed_data.sql"
output_file = "seed_data_temp.sql"

with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
    for line in f_in:
        if line.startswith("INSERT INTO myapp_student"):
            match = re.search(r"'STID-S-(\d{4})'", line)
            if match:
                student_num = int(match.group(1))
                batch_num = (student_num - 1) // 6 + 1
                new_batch = f"Batch {batch_num}"
                
                # Replace the batch value (the third value in the VALUES tuple)
                line = re.sub(r"(VALUES \('[^']+',\s*'[^']+',\s*)'[^']+'", rf"\1'{new_batch}'", line)
        f_out.write(line)

os.replace(output_file, input_file)
print("Batches updated successfully.")
