import shutil
import os
import zipfile
import tarfile
import gzip
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

POLISH_LETTERS = {'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ż': 'z', 'ź': 'z'}

IMAGE_EXTENSIONS = ['JPEG', 'PNG', 'JPG', 'SVG']
VIDEO_EXTENSIONS = ['AVI', 'MP4', 'MOV', 'MKV', 'GIF']
DOCUMENTS_EXTENSIONS = ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX', 'PY']
AUDIO_EXTENSIONS = ['MP3', 'OGG', 'WAV', 'AMR']
APPLICATIONS_EXTENSIONS = ['EXE']
ARCHIVES_EXTENSIONS = ['ZIP', 'GZ', 'TAR']

all_existing_extensions = set()
unrecognized_extensions = set()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def normalize(some_string):  
    result = ""
    for char in some_string:
        if char.lower() in POLISH_LETTERS:
            result += POLISH_LETTERS[char.lower()]
        elif char.isspace() or char.isalnum():
            result += char
        else:
            result += "_"
    return result 

def move_and_normalize_files(file_path, new_folder_name):
    normalized_name = normalize(Path(file_path).stem)
    move_file = os.path.join(os.path.dirname(file_path), new_folder_name)
    move_to = os.path.join(move_file, f"{normalized_name}.{file_path.split('.')[-1]}")
    
    os.makedirs(move_file, exist_ok= True)
    try:
        shutil.move(file_path, move_to)
        logging.debug(f"Moved {file_path} to {move_to}")
    except Exception as e:
        logging.error(f"Failed to move {file_path}: {str(e)}")

def archive_folder_and_move(path, arch_name, new_folder_name):
    arch_path = os.path.join(path, arch_name)
    extracted_archive = os.path.join(path, arch_name.split('.')[0])
    move_file = os.path.join(os.path.dirname(arch_path), new_folder_name)
    move_to = os.path.join(move_file, arch_name.split('.')[0])
    
    try:
        if arch_name.split('.')[-1].upper() == 'ZIP':
            with zipfile.ZipFile(arch_path, 'r') as zip:
                zip.extractall(extracted_archive)
        elif arch_name.split('.')[-1].upper() == 'TAR':
            with tarfile.open(arch_path, 'r') as tar:
                tar.extractall(extracted_archive)
        elif arch_name.split('.')[-1].upper() == 'GZ':
            with gzip.open(arch_path, 'rb') as f_in, open(extracted_archive, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(arch_path)
        os.makedirs(move_file, exist_ok=True)
        shutil.move(extracted_archive, move_to)
        
        logging.debug(f"Archived and moved {arch_name} to {move_to}")
    except Exception as e:
        logging.error(f"Failed to extract and move {arch_name}: {str(e)}")

def process_files_in_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            extension = file.split('.')[-1].upper()
            
            if any(folder in root for folder in ["images", "video_files", "documents", "music", "archives", "unknown_extensions"]):
                continue
            if extension in IMAGE_EXTENSIONS:
                all_existing_extensions.add(extension)
                move_and_normalize_files(file_path, "images")
            elif extension in VIDEO_EXTENSIONS:
                all_existing_extensions.add(extension)
                move_and_normalize_files(file_path, "video_files")
            elif extension in DOCUMENTS_EXTENSIONS:
                all_existing_extensions.add(extension)
                move_and_normalize_files(file_path, "documents")
            elif extension in AUDIO_EXTENSIONS:
                all_existing_extensions.add(extension)
                move_and_normalize_files(file_path, "music")
            elif extension in APPLICATIONS_EXTENSIONS:
                all_existing_extensions.add(extension)
                move_and_normalize_files(file_path, "applications")
            elif extension in ARCHIVES_EXTENSIONS:
                all_existing_extensions.add(extension)
                archive_folder_and_move(root, file, "archives")
            else:
                unrecognized_extensions.add(extension)
                continue
                
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            new_dir_path = os.path.join(root, normalize(dir))
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
                logging.debug(f"Removed empty directory: {dir_path}")
            else:
                os.rename(dir_path, new_dir_path)
                logging.debug(f"Renamed directory {dir_path} to {new_dir_path}")

def process_folder(folder_to_sort):
    start_time = time.time()
    with ThreadPoolExecutor() as executor:
        executor.submit(process_files_in_folder, folder_to_sort)
    end_time = time.time()
    logging.info(f"Sorting process completed in {end_time - start_time} seconds.")
    
if __name__ == "__main__":
    folder_to_sort = input("Enter folder to sort: ")
    process_folder(folder_to_sort)