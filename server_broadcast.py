import socket
import threading
import os
import struct

import server_connection
import main
def update_broadcast_message(server_socket,file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            operation_type = 0  # 0 for add/update
            file_size = os.path.getsize(file_path)
            file_path_encoded = file_path.encode()

            # Prepare the message without the file content
            message_without_file = struct.pack('!I', operation_type) + struct.pack('!Q', file_size) + file_path_encoded
            message_length = len(message_without_file)

            # Send the message length and the message
            server_socket.sendall(struct.pack('!I', message_length))
            server_socket.sendall(message_without_file)

            # Send the file data
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    server_socket.sendall(chunk)
    else:
        # Send delete operation
        operation_type = 1  # 1 for delete
        file_path_encoded = file_path.encode()
        message = struct.pack('!I', operation_type) + struct.pack('!Q', 0) + file_path_encoded
        message_length = len(message)

        # Send the message length and the message
        server_socket.sendall(struct.pack('!I', message_length))
        server_socket.sendall(message)
        print("SEND OUT THE DELETE REQUEST!!!")

    

def delete_broadcast_message(file_path):
    with server_connection.lock:
            for conn in main.socket_array:
                try:
                    send_delete_file_request(conn, file_path)
                except Exception as e:
                    print("Error sending message to client: {}".format(e))


def send_data_over_existing_connection(conn, file_path):  
    with open(file_path,'rb') as file:
        while True:
            data = file.read()
            if not data:
                break
            # get server socket
            send_data = {
                "file_path":file_path,
                "file_data": data,
            }
            server_connection.send_to_client(conn, "small_update", send_data)
    server_connection.send_to_client(conn, "small_update", b'END')

# Chunk the data and then send data over existing connection
def send_chunked_data_over_existing_connection(conn, file_path, chunk_size=1024*1024*5):
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size // chunk_size) + (1 if file_size % chunk_size > 0 else 0)

    with open(file_path,'rb') as file:
        for chunk_num in range(total_chunks):
            data = file.read(chunk_size)
            header = f"{len(data):010d}:{chunk_num:010d}".encode()
            send_data = {
                "file_path":file_path,
                "file_data": data,
            }
            server_connection.send_to_client(conn, "large_update",header+send_data)
    
    # send end of file signal to server
    server_connection.send_to_client(conn, "large_update", b'END')

# send delte request
def send_delete_file_request(conn,file_path):
    send_data = {
                "file_path":file_path,
                "file_data": None,
            }
    server_connection.send_to_client(conn, "delete", send_data)
        

    