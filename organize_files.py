
import os
import shutil

# Directory to move obsolete files to
dest_dir = "_obsolete_files"

# List of files and directories to move
obsolete_items = [
    "gemini",
    "js",
    "app.js",
    "index.js",
    "Dockerfile",
    "runtime.txt",
    "BACKUP",
    "testeo",
    "backend",
    ".gitignore.txt",
    "Copia de seguridad de TITULOS.xlk",
    "database_fix.py",
    "verificar_db.py",
    "ejemplos.py",
    "__pycache__",
    "KEY_GEMINI.py",
    "config.js",
    "-r",
    "-tree",
    "run.ps1",
    "verificar_db.py",
    ".gitignore`.txt",
    "config.js",
    "conversaciones.db",
    "database_fix.py",
    "ejemplos.py",
    "excel_to_json.py",
    "index.js",
    "KEY_GEMINI.py",
]

# Create the destination directory if it doesn't exist
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

for item in obsolete_items:
    if os.path.exists(item):
        try:
            shutil.move(item, os.path.join(dest_dir, item))
            print(f"Moved {item} to {dest_dir}")
        except Exception as e:
            print(f"Error moving {item}: {e}")
    else:
        print(f"{item} does not exist, skipping.")

print("File organization complete.")
