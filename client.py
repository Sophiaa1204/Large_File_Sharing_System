
import pickle
import threading
import socket
import sys
import time
import hashlib
import struct
import os
from xxlimited import new
import server_connection

class Client:
    # Class variable
    server_ip=""
    server_port=12345
    thisip=""
    thisport=23456
    neighbors=[]
    server_socket=None
    connected_addr=[]
    received=[]
    # Constructor (initializer) method
    def __init__(self, server_ip,server_port,thisip,thisport):
        # Instance variables
        self.server_ip=server_ip
        self.server_port=server_port
        self.thisip=thisip
        self.thisport=thisport
        self.lock = threading.Lock()
    # Instance method
    def init_socket(self):
        this_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        this_address = ("0.0.0.0", self.thisport)  # may need change
        this_socket.bind(this_address)
        this_socket.listen(1000)
        return this_socket
    def init_connection_with_server(self):
        try:
             this_socket_connect_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
             this_socket_connect_server.connect((self.server_ip,self.server_port))
             this_address_str=self.thisip+" "+str(self.thisport)
             this_socket_connect_server.send(pickle.dumps(this_address_str))
             self.server_socket=this_socket_connect_server
             return this_socket_connect_server
        except:
            exit(0)
    def recv_neighbor_from_server(self):
         thisconnectserver=self.init_connection_with_server()
         while True:
          neighborarr=thisconnectserver.recv(4096)
          try:
              neighborarr=pickle.loads(neighborarr)
          except:
              print("N")
              continue
          if type(neighborarr)!=type([]):
              print("f")
              continue
          print(neighborarr)
          print(self.thisip)
          for neighbor in neighborarr:
                 self.neighbors.append(neighbor)
          if len(self.neighbors)>=2:
              break
    def start_peer_connection_server(self):
        thisserverside=self.init_socket()
        print("bind sucesss!")
        print("IN Start_peer_connection_server")
        while True:
            peer_socket,peer_addr=thisserverside.accept()
            print(peer_addr)
            with self.lock:
                self.connected_addr.append(peer_addr)
    def start_peer_connection_client(self):
       print("IN Start_peer_connection_client")
       while True:
        for neighbor in self.neighbors:
            if neighbor[0]!=self.thisip:
                with self.lock:
                    if self.connected_addr.count(neighbor[0])==0:
                        neighborsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        print((neighbor[0],neighbor[1]))
                   
                        neighborsocket.connect((neighbor[0],neighbor[1]))
                        self.connected_addr.append(neighbor[0])
                    

                   
    def start_peer_connection_thread(self):
        print("IN START THREADS")
        thread=threading.Thread(target=self.start_peer_connection_server)
        thread.start()
        # Pause for a specified number of seconds to avoid double connection
        pause_duration = 5  # Pause for 5 seconds, for example
        time.sleep(pause_duration)
        thread2=threading.Thread(target=self.start_peer_connection_client)
        thread2.start()
    def notify_server(self, file_path):
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            operation_type = 0  # 0 for add/update
            file_size = os.path.getsize(file_path)
            file_path_encoded = file_path.encode()

            # Prepare the message without the file content
            message_without_file = struct.pack('!I', operation_type) + struct.pack('!Q', file_size) + file_path_encoded
            message_length = len(message_without_file)

            # Send the message length and the message
            self.server_socket.sendall(struct.pack('!I', message_length))
            self.server_socket.sendall(message_without_file)

            # Send the file data
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(1024)
                    if not chunk:
                        break
                    self.server_socket.sendall(chunk)
        else:
            # Send delete operation
            operation_type = 1  # 1 for delete
            file_path_encoded = file_path.encode()
            message = struct.pack('!I', operation_type) + struct.pack('!Q', 0) + file_path_encoded
            message_length = len(message)

            # Send the message length and the message
            self.server_socket.sendall(struct.pack('!I', message_length))
            self.server_socket.sendall(message)

    # # operation type 0 add/update 1 delete
    #   print("send once!!!!!")
    #   if self.server_socket is None:
    #      return
    #   if os.path.exists(file_path):
    #     if os.path.getsize(file_path)==0:
    #         return
    #     self.server_socket.send(pickle.dumps(0))
    #     file_size = os.path.getsize(file_path)
    #     self.server_socket.send(pickle.dumps(file_size))
    #     print("size: " + str(file_size))
    #     self.server_socket.send(pickle.dumps(file_path))
    #     print("file path:"+file_path)
    #     # Read and send the file data in 1024-byte chunks
    #     all_length=0
    #     with open(file_path, 'rb') as file:
    #         chunk_size = 1024
    #         while True:
    #             chunk = file.read(chunk_size)
    #             self.server_socket.send(chunk)
    #             all_length+=len(chunk)
    #             if all_length>=file_size:
    #                 file.close()
    #                 break
    #   else:
    #     self.server_socket.send(pickle.dumps(1))
    #     file_size =0
    #     self.server_socket.send(pickle.dumps(file_size))
    #     self.server_socket.send(pickle.dumps(file_path))

    def calculate_md5(self,file_path):
       """Calculate the MD5 hash of a file."""
       hash_md5 = hashlib.md5()
       with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
       return hash_md5.hexdigest()
    
    def client_receive_server_updates(self):
        print("IN CLIENT RECEIVE SERVER UPDATE")
        message = server_connection.pre_process_message(self.server_socket)
        print("IN HANDLE CLIENT MESSAGE!!CLIENT")
        message_type = message['type']
        data = message['data']
        print(message_type)
        print(data)
        print("__________")
        if message_type == 0:
            file_path = data['file_path']
            file_data = data['file_data']
            print("BEFORE HANDLE RECEIVE ADD CLIENG")
            print(file_path,file_data)
            with open(file_path, 'wb') as file:
                file.write(file_data)
            with self.lock:
                self.received.append(file_path)
        if message_type == 1:
            file_path = data['file_path']
            print("BEFORE REMOVE FILE!")
            if os.path.exists(file_path):
                os.remove(file_path)
                print("SUCCESSFULLY REMOVE AT CLIENT SIDE")
                self.received.remove(data)
        
        print(f"File received completely.Received file list is {self.received}")
                
    def start_file_monitor(self,directory_path, interval=0.5):
       current_list=os.listdir(directory_path)
       current_md5_list=[]
       for file in current_list:
          current_md5_list.append(self.calculate_md5("share/"+file))
       while True:
           time.sleep(2)
           new_list_unfiltered=os.listdir(directory_path)
           new_list = []
           for file in new_list_unfiltered:
               if ("share/"+file) in self.received:
                #    print("share/"+file+"in received")
                   continue
               else:
                   new_list.append(file)
           if len(new_list)==len(current_list):
               # update
               current_md5_list_new=[]
               for file in new_list:
                 current_md5_list_new.append(self.calculate_md5("share/"+file))
               for i in range(len(current_md5_list_new)):
                   if current_md5_list.count(current_md5_list_new[i])==0:
                       servernotifythread=threading.Thread(target=self.notify_server,args=("share/"+new_list[i],))
                       servernotifythread.start()
                       print("file changed A")
               current_list=new_list
               current_md5_list=current_md5_list_new
           else:
               # delete
               if len(new_list)<len(current_list):
                  new_list = new_list_unfiltered
                  for file_d in current_list:
                      if new_list.count(file_d)==0:
                          servernotifythread=threading.Thread(target=self.notify_server,args=("share/"+file_d,))
                          servernotifythread.start()
                          print("file changed B")
               else:
                # add
                   for file_a in new_list:
                       if current_list.count(file_a)==0:
                           servernotifythread=threading.Thread(target=self.notify_server,args=("share/"+file_a,))
                           servernotifythread.start()
                           print("file changed C")
               print(len(current_list))
               current_list=new_list
               print(len(current_list))
               new_md5_list=[]
               for file in current_list:
                   new_md5_list.append(self.calculate_md5("share/"+file))
               current_md5_list=new_md5_list

        
thisnode=Client(sys.argv[1],int(sys.argv[2]),sys.argv[3],int(sys.argv[4]))
thisnode.recv_neighbor_from_server()
thisnode.start_peer_connection_thread()
cwd = os.getcwd()

    # Define the directory name
directory_name = "share"
directory_path = os.path.join(cwd, directory_name)
if os.path.exists(directory_path):
     for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {filename}: {e}")
else:
    try:
            os.mkdir(directory_path)
    except Exception as e:
            print(f"Error creating directory {directory_name}: {e}")
thread2=threading.Thread(target=thisnode.client_receive_server_updates)
thread2.start()
thisnode.start_file_monitor(directory_path="share")
