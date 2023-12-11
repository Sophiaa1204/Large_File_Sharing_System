import time
import os
import socket
import client_p2p_connection

file_status_dict = {}

def update_file_status(file_path):
    current_time = time.time()
    file_status_dict[file_path] = current_time

def remove_file_status(file_path):
    del file_status_dict[file_path]

def check_file_status(file_path):
    if file_path in file_status_dict:
        operation_type, timestamp = file_status_dict[file_path]
        return True, operation_type, timestamp
    return False, None, None

def handle_receive_update(save_path, file_data):
    result, timestamp = check_file_status(save_path)
    if result:
        with open(save_path, 'wb') as file:
            file.write(file_data)
    # update the file status
        file_path = save_path
        if file_path in file_status_dict:
            update_file_status(file_path)
        else:
            update_file_status(file_path)
        log_server_operation(file_path, "changed",file_data)

def handle_receive_add(save_path, file_data):
    result, timestamp = check_file_status(save_path)
    if result:
        with open(save_path, 'wb') as file:
            file.write(file_data)
    # update the file status
        file_path = save_path
        if file_path in file_status_dict:
            update_file_status(file_path)
        else:
            update_file_status(file_path)
        log_server_operation(file_path, "added", file_data)

def handle_receive_delete(delete_path):
    result, timestamp = check_file_status(delete_path)

    if result:
        if os.path.exists(delete_path):
            os.remove(delete_path)
            remove_file_status(delete_path)
            log_server_operation(delete_path, "added", None)

def log_server_operation(file_path, change_type, buffer=None):
    log_entry = f"File Path: {file_path}, Change Type: {change_type}, Buffer: {buffer}\n"
    with open("server_operations_log.txt", "a") as log_file:
        log_file.write(log_entry)


