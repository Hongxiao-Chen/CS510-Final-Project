import os
import hashlib
import time


def _get_folder_info(directory):
    file_info = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            # last modified time
            modified_time = os.path.getmtime(filepath)
            modified_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modified_time))
            file_info.append((filename, modified_time_str))
    return file_info


def get_folder_hash(directory):
    """
    Generate hash for knowledge base
    Args:
        directory: folder path

    Returns:
        {filename}_{last_modified_time} hash
    """
    file_info = _get_folder_info(directory)
    file_info_sorted = sorted(file_info)

    combined_str = ''.join([f"{filename}_{modified_time}" for filename, modified_time in file_info_sorted])


    hash_object = hashlib.sha256(combined_str.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig


if __name__ == "__main__":
    directory = "D:\\CS\\CS510\\final-project\\data\\inputdata\\Test"

    hash_value = get_folder_hash(directory)

    print(f"Hash value: {hash_value}")
