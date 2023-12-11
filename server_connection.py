import socket
import threading
# import pickle
import pickle
import sys
import server_change_receiver
lock=threading.Lock
import struct
import main

# server socket is a global variable
# Wrapper method to send data to client
def send_to_client(server_socket, message_type, data):
    message = {
        'type': message_type,
        'data': data
    }
    serialized_message = pickle.dumps(message)
    message_length = struct.pack('!I', len(serialized_message))
    server_socket.sendall(message_length + serialized_message)
    # server_socket.sendall(serialized_message)

def handle_client_message(message, client_socket):
    print("IN HANDLE CLIENT MESSAGE!!")
    message_type = message['type']
    data = message['data']
    print(message_type)
    print(data)
    print("__________")
    if message_type == 'add':
        file_path = data['file_path']
        file_data = data['file_data']
        server_change_receiver.handle_receive_add(file_path,file_data)
    if message_type == 'small_update':
        file_path = data['file_path']
        file_data = data['file_data']
        server_change_receiver.handle_receive_update(file_path,file_data,client_socket)
    if message_type == 'large_update':
        file_path = data['file_path']
        file_data = data['file_data']
        server_change_receiver.handle_receive_update(file_path,file_data)
    if message_type == 'delete':
        file_path = data['file_path']
        server_change_receiver.handle_receive_delete(file_path)
    else:
        print("Unknown message type received")

def receive_from_client(client_socket):
    # Read message length and unpack it into an integer
    raw_message_length = recvall(client_socket, 4)
    if not raw_message_length:
        return None
    message_length = struct.unpack('!I', raw_message_length)[0]
    
    # Read the message data based on the message length
    serialized_message = recvall(client_socket, message_length)
    if not serialized_message:
        return None
    
    message = pickle.loads(serialized_message)
    return message

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    buffer_size = 4096  # Use a sensible buffer size
    while len(data) < n:
        print(f"remaining length is {n-len(data)}")
        packet = sock.recv(min(buffer_size, n - len(data)))
        if not packet:
            print("return None")
            return None
        data.extend(packet)

        # Optional: Update progress less frequently
        if len(data) % (buffer_size * 10) == 0:
            print(f"Received {len(data)} of {n} bytes")

    print("IN RECVALL!")
    return data

def pre_process_message(server_socket,client_socket):
    # TIMEOUT_DURATION = 100

    # server_socket.settimeout(TIMEOUT_DURATION)
    raw_message_length = recvall(client_socket, 4)
    if not raw_message_length:
        return None
   
    message_length = struct.unpack('!I', raw_message_length)[0]
    print("The raw message length is:", message_length)

    # Read the message data based on the message length
    print("Before serialize the main part!!!!")
    message_data = recvall(client_socket, message_length)
    print("After serialize the main part!!!!")
    if message_data is None:
        return None
    operation_type, file_size = struct.unpack('!IQ', message_data[:12])
    file_path = message_data[12:].decode()  # assuming the rest of the message is the file path

    print(operation_type,file_size,file_path)

    return ""

# to avoid timeout
# def pre_process_message(server_socket,client_socket):
#     TIMEOUT_DURATION = 100
 
#     server_socket.settimeout(TIMEOUT_DURATION)
#     serialized_message = client_socket.recv(4096)
#     message = pickle.loads(serialized_message)
#     print("pre called!!!!!!")
#     print(message)
#     message_type = message['type']
#     if message_type in ['small_update', 'large_update']:
#         file_data = b''
#         file_data += message['data']['file_data']
#         while True:
#             try:
#                 serialized_message_sub = client_socket.recv(4096)
#                 message_sub = pickle.loads(serialized_message_sub)
#                 if message_sub['data'] == b'END':
#                     break
#                 else:
#                     print("received data!!!!!!!!")
#                     file_data += message_sub['data']['file_data']
#             except socket.timeout:
#                 print("Timeout occurred while receiving file data.")
#                 # Handle Timeout
#                 break
#             finally:
#                 server_socket.settimeout(None)  # 将超时设置回无限制

#         file_path = message['data']['file_path']
#         message['data'] = {
#             "file_path": file_path,
#             "file_data": file_data,
#         }

#     return message

def handle_client(server_socket,client_socket):
    while True:
         message = pre_process_message(server_socket,client_socket)
         handle_client_message(message,client_socket)
