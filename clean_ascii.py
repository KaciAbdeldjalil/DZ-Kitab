import os
import re

def clean_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace non-ASCII characters with ASCII equivalents or just remove them
        # E.g., 'à' -> 'a', 'é' -> 'e', etc.
        # For simplicity, we can just filter them out if they are emojis or special symbols
        clean_content = content.encode('ascii', 'ignore').decode('ascii')
        
        if content != clean_content:
            with open(file_path, 'w', encoding='ascii') as f:
                f.write(clean_content)
            print(f"Cleaned {file_path}")
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")

app_dir = 'c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend/app'
for root, dirs, files in os.walk(app_dir):
    for file in files:
        if file.endswith('.py'):
            clean_file(os.path.join(root, file))
