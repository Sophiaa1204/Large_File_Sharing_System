import socket
import pickle
import threading
from config import server_ip, server_port
import client_change_receiver
import client_file_monitor
import struct
# one thread for each pair to pair connection
lock = threading.Lock()
# store info about established pair connection
global pair_connections
pair_connections=[]
global conn_server_socket
conn_server_socket = None
global neighborips
global client_id
def getConnection():
    while conn_server_socket==None:
        pass
    return conn_server_socket
# Method to handle received message from the server
def handle_received_message(message):
    print("In handle received message!!!!!")
    if message==None:
        return
    message_type = message['type']
    data = message['data']
    if message_type == 'add':
        file_path = data['file_path']
        file_data = data['file_data']
        client_change_receiver.handle_receive_add(file_path,file_data)
    elif message_type == 'small_update':
        file_path = data['file_path']
        file_data = data['file_data']
        client_change_receiver.handle_receive_update(file_path,file_data)
    elif message_type == 'large_update':
        file_path = data['file_path']
        file_data = data['file_data']
        client_change_receiver.handle_receive_update(file_path,file_data)
    elif message_type == 'delete':
        file_path = data['file_path']
        client_change_receiver.handle_receive_delete(file_path)
    elif message_type == 'confirmation':
        result = message['data']['result']
        if result == "SUCCESS":
            print("File {} transferred successfully.".format(data['file_path']))
            return
        if result == "FAIL":
            file_path = message['data']['file_path']
            # The only possibility for a failed change is that the file has been deleted
            client_change_receiver.handle_receive_delete(file_path)
    else:
        print("Unknown message type received")

# Method to create a new thread for each p2p connection
def handle_client_connection(client_server,ips:[]):
   for iplist in ips:
       try:
           ip=iplist[0]
           port=iplist[1]
           client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           client_socket.connect((ip, port))
           with lock:
               pair_connections.append(client_socket)

           # # TODO: Add logic for election
           # while True:
           #     message = client_socket.recv(4096)

       except Exception as e:
           print("Could not connect to {}:{} - {}".format(ip, port, e))

       finally:
           client_socket.close()
           with lock:
               pair_connections.remove(client_socket)
   while True:
       c_socket,c_address=client_server.accept()
# A wrapper to send message to server
# Two types of message: update_notifications, delete_notifications
def send_to_server(server_socket, message_type, data):
    message = {
        'type': message_type,
        'data': data
    }
    serialized_message = pickle.dumps(message)
    # ensure the safety of shared resources
    with lock:
        message_length = struct.pack('!I', len(serialized_message))
        server_socket.sendall(message_length + serialized_message)
        # server_socket.sendall(serialized_message)

def client_entry(server_ip,server_port,client_ip,client_port):
   try:
       print("start binding called")
       # load the config info
       server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       server_address = (client_ip, client_port)
       server_socket.bind(server_address)
       print("after binding 1")
       server_socket.listen(1000)
       server_ip = server_ip
       server_port = server_port
       # connect to the server
       print("after binding")
       client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       try:
           client_socket.connect((server_ip, server_port))
           client_socket.send(pickle.dumps((client_ip+" "+str(client_port))))
       except:
           print("can not connect to server")
           client_socket.close()
           exit(0)
       dumpediplist=client_socket.recv(4096)
       global neighborips
       neighborips=pickle.loads(dumpediplist)
       print("thread start")
       connectionhandler=threading.Thread(target=handle_client_connection,args=(((server_socket,neighborips))))
       connectionhandler.start()
       # receive data from the server
       print("client connect success!")
       global conn_server_socket
       conn_server_socket=client_socket
       filehandler=threading.Thread(target=client_file_monitor.monitor_directory,args=(("share",2)))
       filehandler.start()
       while True:
           print("pre good!")
           message = pre_process_message(server_socket,client_socket)
           print("pre good2!")
           handle_received_message(message)
           print("receive good!")
   except Exception as e:
        print(f"An exception occurred: {str(e)}")
# to avoid timeout
# refactor 
# almost the same as the function in server connection
def pre_process_message(client_server,server_socket):
    TIMEOUT_DURATION = 100
 
    server_socket.settimeout(TIMEOUT_DURATION)
    serialized_message = server_socket.recv(4096)
    message = pickle.loads(serialized_message)
    print(message)
    if type(message)==type([]):
         connectionhandler=threading.Thread(target=handle_client_connection,args=(((client_server,message))))
         connectionhandler.start()
         return
    message_type = message['type']
    if message_type in ['small_update', 'large_update']:
        file_data = b''
        file_data += message['type']['file_data']
        while True:
            try:
                serialized_message_sub = server_socket.recv(4096)
                message_sub = pickle.loads(serialized_message_sub)
                if message_sub['data'] == b'END':
                    break
                else:
                    file_data += message_sub['data']['file_data']
            except socket.timeout:
                print("Timeout occurred while receiving file data.")
                # Handle Timeout
                break
            finally:
                server_socket.settimeout(None)  

        file_path = message['data']['file_path']
        message['data'] = {
            "file_path": file_path,
            "file_data": file_data,
        }

    return message
