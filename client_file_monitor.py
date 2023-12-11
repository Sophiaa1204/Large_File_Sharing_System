# File monitor has a own thread
# File change detection
import hashlib
import os
import time
# from client_change_sender import send_data_over_existing_connection, send_chunked_data_over_existing_connection, send_delete_file_request
import client_change_sender
# Calculate the MD5 checksum of the file at the given path
def calculate_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        buffer = file.read()
        hasher.update(buffer)
    return hasher.hexdigest()

# Use recurssion to get all file pathes
def get_all_paths(directory_path,all_file_paths=None):
    if all_file_paths == None:
        all_file_paths = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path,filename)
        if os.path.isfile(file_path):
            all_file_paths.append(file_path)
        if os.path.isdir(file_path):
            get_all_paths(file_path,all_file_paths)
    return all_file_paths

# This function returns a dictionary representing the current state of the directory
# This dictionary maps file names to their MD5 checksums
def get_directory_state(directory_path):
    directory_state = {}
    all_files = get_all_paths(directory_path)

    for file_path in all_files:
        directory_state[file_path] = calculate_md5(file_path)
    return directory_state

# A function to record file change history in change_log.txt
def log_change(file_path, change_type, source):
    with open("change_log.txt","a") as log_file:
        log_file.write("{}: {} was {} by {}\n".format(time.ctime(),file_path,change_type,source))

# This function aims at continuously monitoring the given directory
# change the interval value to reset how often a directory is checked (in seconds)
# if a change is detected, the new file will be sent in the binary form along with its corresponding path(in JSON format)
# handle change is a call back function
def monitor_directory(directory_path, interval=10):
    last_state = None
    while True:
        current_state = get_directory_state(directory_path)
        changes = []
        print("start while true loop!!!!")
        if last_state is not None:
            added = current_state.keys() - last_state.keys()
            removed = last_state.keys() - current_state.keys()
            modified = {file_path for file_path in current_state.keys() & last_state.keys()
                        if current_state[file_path] != last_state[file_path]}
            
            for file_path in added:
                source = determine_change_source(file_path, "added")
                log_change(file_path, "added", source)
                # only send the request if the source of change is not central server
                if source != "central_server":
                    changes.append({"action":"added", "file_path":file_path})
            for file_path in removed:
                source = determine_change_source(file_path,"removed")
                log_change(file_path, "removed", source)
                if source != "central_server":
                    changes.append({"action":"removed","file_path":file_path})
            for file_path in modified:
                with open(file_path,'rb') as f:
                    buffer = f.read()
                    source = determine_change_source(file_path,"changed")
                    log_change(file_path, "changed", source)
                    if source != "central_server":
                        changes.append({"action":"modified","file_path":file_path,"buffer":buffer})
            
            if len(changes)>0:
                # The change will be processed by chunker
                print("change detected")
                handle_change(changes)
        
        last_state = current_state
        time.sleep(interval)

# Method to determine the source of change
# File name can't be the same
# To avoid multi-threading issue
def determine_change_source(file_path, change_type, buffer=None):
    with open("server_operations_log.txt","r") as log:
        for line in log:
            if file_path in line and change_type in line and buffer in line:
                return "central_server"
    return "local"

# callback function that responsible to send the response to all nodes within the network (a dummy function now)
def handle_change(changes):
    print(changes)
    for change in changes:
        action = change["action"]
        file_path = change["file_path"]

        if action == "removed":
            client_change_sender.send_delete_file_request(file_path) # send delete request
            return
        else:
            # determine the size of the file, if exceed the threshold, then chunck it
            file_size = os.path.getsize(file_path)
            max_size = 1024 * 1024 * 5

            if file_size > max_size:
                print("small change A")
                client_change_sender.send_chunked_data_over_existing_connection(file_path)
            else:
                print("large change B")
                client_change_sender.send_data_over_existing_connection(file_path)

        

# How to use this monitor
# directory_to_monitor = "" # change the directory here
# monitor_directory(directory_to_monitor)