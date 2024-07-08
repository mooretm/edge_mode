
from pathlib import Path
import os

import csv

_path = r'C:\Users\MooTra\OneDrive - Starkey\Desktop\all_responses'
files = Path(_path).glob('*.csv')
files = list(files)
print(f"\nfield: Found {len(files)} files")


# Get just last rows
comment_list = []
for file in files:
    with open(file, 'r') as f:
        try:
            final_row = f.readlines()[-1]
            
            comment_list.append(final_row)
        except UnicodeDecodeError as e:
            print(f"\nUnicode error in: {os.path.basename(file)}")
            #print(e)
            
# Get non-empty rows
comments = []
for comment in comment_list:
    if len(comment.split()) > 1:
        comments.append(comment)


# Write new file with comments
with open('just_comments.csv', 'w', newline='\n') as f:
    writer = csv.writer(f)
    writer.writerow('Comment')
    writer.writerow(comments)


