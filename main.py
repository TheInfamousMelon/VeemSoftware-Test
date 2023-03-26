import os
import shutil
import time
import logging

# Set up directory paths
SOURCE_DIR = input ("Choose the Source directory")
BACKUP_DIR = input ("Choose the Backup directory")
SOFT_DELETE_DIR = input ("Choose the Soft Delete directory")

# Let the user choose the period of time between sync (in seconds)
period = int(input("Enter the sync period (in seconds): "))

# Set up logging
logging.basicConfig(filename='sync.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logging.getLogger().addHandler(console)

# Create backup and soft delete folders if they don't exist
if not os.path.exists(BACKUP_DIR):
    os.mkdir(BACKUP_DIR)

if not os.path.exists(SOFT_DELETE_DIR):
    os.mkdir(SOFT_DELETE_DIR)

while True:
    # Log that sync has been triggered
    logging.info('Sync triggered')

    # Sync Source and Backup
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Create corresponding folder in backup if it doesn't exist
        backup_dir = os.path.join(BACKUP_DIR, os.path.relpath(root, SOURCE_DIR))
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            if not files and not dirs:
                logging.info(f'Copying empty directory {os.path.relpath(root, SOURCE_DIR)}')

        for file in files:
            source_path = os.path.join(root, file)
            backup_path = os.path.join(backup_dir, file)

            # Check if file needs to be copied or updated
            if os.path.exists(backup_path):
                if os.path.getmtime(source_path) > os.path.getmtime(backup_path):
                    logging.info(f'Updating {file}')
                    shutil.copy2(source_path, backup_path)
            else:
                logging.info(f'Copying {file}')
                shutil.copy2(source_path, backup_path)

    # Delete files from Backup that no longer exist in Source
    for root, dirs, files in os.walk(BACKUP_DIR):
        for file in files:
            backup_path = os.path.join(root, file)
            source_path = os.path.join(SOURCE_DIR, os.path.relpath(root, BACKUP_DIR), file)

            if not os.path.exists(source_path):
                soft_delete_dir = os.path.join(SOFT_DELETE_DIR, os.path.relpath(root, BACKUP_DIR))
                if not os.path.exists(soft_delete_dir):
                    os.makedirs(soft_delete_dir)

                logging.info(f'Moving {file} to SoftDelete')
                shutil.move(backup_path, os.path.join(soft_delete_dir, file))

        for directory in dirs:
            backup_dir = os.path.join(root, directory)
            source_dir = os.path.join(SOURCE_DIR, os.path.relpath(backup_dir, BACKUP_DIR))

            if not os.path.exists(source_dir):
                soft_delete_dir = os.path.join(SOFT_DELETE_DIR, os.path.relpath(backup_dir, BACKUP_DIR))
                if not os.path.exists(soft_delete_dir):
                    os.makedirs(soft_delete_dir)

                logging.info(f'Moving {directory} to SoftDelete')
                shutil.move(backup_dir, os.path.join(soft_delete_dir, directory))

    # Log that sync has completed
    logging.info('Sync complete')

    # Script is paused for the period of time that the user inputs
    time.sleep(period)
