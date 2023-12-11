import pickle
import socket
import os
import client_p2p_connection
# Send data over existing connection
def send_data_over_existing_connection(file_path):  
    print("change calle!!!!!!!!!")
    with open(file_path,'rb') as file:
        print("file OK!!!!!!!!!")
        while True:
            print("loop enter OK!!!!!!")
            data = file.readline()
            print(data)
            if not data:
                print("data wrong!!!!!!!!!!!!!!!")
                break
            # get server socket
            send_data = {
                "file_path":file_path,
                "file_data": data,
            }
            conn = client_p2p_connection.getConnection()
            print("send once!!!!!!")
            client_p2p_connection.send_to_server(conn, "small_update", send_data)
    client_p2p_connection.send_to_server(conn, "small_update", b'END')
    print("send all!!!!!!")
    # wait for the server to respond
    # response = conn.recv(1024).decode()
    # if response == 'SUCCESS':
    #     print("File {} transferred successfully.".format(file_path))
    #     return
    # if response == 'RESEND':
    #     send_data_over_existing_connection(file_path, count=count+1)

# Chunk the data and then send data over existing connection
def send_chunked_data_over_existing_connection(file_path, chunk_size=1024*1024*5):
    file_size = os.path.getsize(file_path)
    total_chunks = (file_size // chunk_size) + (1 if file_size % chunk_size > 0 else 0)
    conn = client_p2p_connection.getConnection()

    with open(file_path,'rb') as file:
        for chunk_num in range(total_chunks):
            data = file.read(chunk_size)
            header = f"{len(data):010d}:{chunk_num:010d}".encode()
            header=pickle.dumps(header)
            send_data = {
                "file_path":file_path,
                "file_data": data,
            }
            send_data=pickle.dumps(send_data)
            client_p2p_connection.send_to_server(conn, "large_update",header+send_data)
    
    # send end of file signal to server
    client_p2p_connection.send_to_server(conn, "large_update", b'END')
    print("send sucessb!!!!!!")
# send delte request
def send_delete_file_request(file_path):
    conn = client_p2p_connection.getConnection()
    send_data = {
                "file_path":file_path,
                "file_data": None,
            }
    client_p2p_connection.send_to_server(conn, "delete", send_data)
    print("send sucessc!!!!!!")