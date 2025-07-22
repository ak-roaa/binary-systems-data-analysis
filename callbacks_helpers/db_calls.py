import os
import re
import pandas as pd
import string


def inspect_db(db_path):
    """
    Inspects a given directory containing data about different systems and organizes
    the file paths of system-related `.l` and `.mat` files into a dictionary.

    Args:
        db_path (str): The path to the directory containing a subdirectory for each system.

    Returns:
        dict: A dictionary where the keys are system names (subdirectory names), and the values
              are lists containing two sorted lists:
              - One list of `l` file paths.
              - One list of `mat` file paths.
    """
    systems_dict = {}

    for system in os.listdir(db_path):
        system_path = os.path.join(db_path, system)
        
        if os.path.isdir(system_path):
            # Separate files by starting letter and collect file paths
            l_files = sorted([f for f in os.listdir(system_path) if f.startswith('l')], key=lambda f: f[-1])
            mat_files = sorted([f for f in os.listdir(system_path) if f.startswith('mat')], key=lambda f: f[-1])

            # Add system to dictionary
            systems_dict[system] = [l_files, mat_files]
    
    return systems_dict    


def add_system(db_path, new_system_name, files_info):
    """
    Creates a new subfolder inside the given db_path and saves the files inside it.
    The filenames must follow specific formats:
    - `l_num_num_letter` for l files
    - `mat_num_num_mt_letter` for mat files
    
    Args:
    - db_path (str): The path to the parent data folder.
    - new_system_name (str): The name of the new subfolder to create.
    - files_info (list): A list of dictionaries of the form  {"filename": filename, "content": content}
    
    Returns:
    - str: Success or error message.
    """ 
    # Define the regex patterns for valid filenames
    l_file_pattern = r"^l_\d+_\d+_[A-Z]$"  # l_num_num_letter
    mat_file_pattern = r"^mat_\d+_\d+_mt_[A-Z]$"  # mat_num_num_mt_letter

    # Create the full path for the new subfolder
    new_system_path = os.path.join(db_path, new_system_name)
    
    # Check if the subfolder already exists
    if not os.path.exists(new_system_path):
        os.makedirs(new_system_path)  # Create the folder

    # Loop through the list of files and save them in the new folder
    for file in files_info:
        # Validate the filename format using regex
        file_name = file["filename"]
        if not re.match(l_file_pattern, file_name) and not re.match(mat_file_pattern, file_name):
            return f"Error: File '{file_name}' must be of the format 'l_num_num_letter' or 'mat_num_num_mt_letter'."

        # Save the file if the format is valid
        file_path = os.path.join(new_system_path, file_name)
        
        try:
            with open(file_path, 'wb') as f:
                f.write(file["content"])
        except Exception as e:
            return f"Error saving file '{file_name}': {str(e)}"

    return f"New system successfully saved in the database '{new_system_name}'."


def add_file_to_system(db_path, system_name, filename, content_bytes):
    """
    Save a file to an existing system’s directory.

    Given the base folder path, a system name, a filename, and the decoded
    file bytes, writes the file under the specified system subdirectory.

    Args:
        db_path (str): Path to the top-level data storage directory.
        system_name (str): Name of the system (must already exist).
        filename (str): Filename to assign (including extension).
        content_bytes (bytes): File data in raw bytes.

    Raises:
        FileNotFoundError: If the system directory does not exist.
        OSError: If writing the file fails (e.g., due to permissions or disk issues).
    """
    system_path = os.path.join(db_path, system_name)
    # Ensure the system directory exists
    if not os.path.isdir(system_path):
        raise FileNotFoundError(f"System '{system_name}' not found in '{db_path}'.")
    # Write the bytes to file
    file_path = os.path.join(system_path, filename)
    with open(file_path, 'wb') as f:
        f.write(content_bytes)


def delete_file_from_system(db_path, system_name, filename):
    """
    Delete a file from the specified system’s directory.

    Raises:
        FileNotFoundError: If the system directory or file doesn’t exist.
        OSError: If deletion fails (e.g. due to permissions).
    """
    system_path = os.path.join(db_path, system_name)
    if not os.path.isdir(system_path):
        raise FileNotFoundError(f"System '{system_name}' not found in '{db_path}'.")
    file_path = os.path.join(system_path, filename)
    try:
        os.remove(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found in system '{system_name}'.")
