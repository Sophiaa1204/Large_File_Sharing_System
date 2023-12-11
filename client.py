
import pickle
import threading
import socket
import sys
import time
import hashlib
import os
from xxlimited import new
class Client:
    # Class variable
    server_ip=""
    server_port=12345
    thisip=""
    thisport=23456
    neighbors=[]
    server_socket=None
    # Constructor (initializer) method
    def __init__(self, server_ip,server_port,thisip,thisport):
        # Instance variables
        self.server_ip=server_ip
        self.server_port=server_port
        self.thisip=thisip
        self.thisport=thisport
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
          if len(self.neighbors)>2:
              break
    def start_peer_connection_server(self):
        thisserverside=self.init_socket()
        print("bind sucesss!")
        while True:
            peer_socket,peer_addr=thisserverside.accept()
    def start_peer_connection_client(self):
       connected_addr=[]
       while True:
        for neighbor in self.neighbors:
            if neighbor[0]!=self.thisip:
                if connected_addr.count(neighbor[0])==0:
                    neighborsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print((neighbor[0],neighbor[1]))
                    try:
                        neighborsocket.connect((neighbor[0],neighbor[1]))
                        connected_addr.append(neighbor[0])
                    except Exception as e:
                        print(f"Can't connect with the neighbor {e}")

                   
    def start_peer_connection_thread(self):
        thread=threading.Thread(target=self.start_peer_connection_server)
        thread.start()
        thread2=threading.Thread(target=self.start_peer_connection_client)
        thread2.start()
    def notify_server(self, file_path):
    # operation type 0 add/update 1 delete
      print("send once!!!!!")
      if self.server_socket is None:
         return
      if os.path.exists(file_path):
        if os.path.getsize(file_path)==0:
            return
        self.server_socket.send(pickle.dumps(0))
        file_size = os.path.getsize(file_path)
        self.server_socket.send(pickle.dumps(file_size))
        print("size: " + str(file_size))
        self.server_socket.send(pickle.dumps(file_path))
        print("file path:"+file_path)
        # Read and send the file data in 1024-byte chunks
        all_length=0
        with open(file_path, 'rb') as file:
            chunk_size = 1024
            while True:
                chunk = file.read(chunk_size)
                self.server_socket.send(chunk)
                all_length+=len(chunk)
                if all_length>=file_size:
                    file.close()
                    break
      else:
        self.server_socket.send(pickle.dumps(1))
        file_size =0
        self.server_socket.send(pickle.dumps(file_size))
        self.server_socket.send(pickle.dumps(file_path))
    def calculate_md5(self,file_path):
       """Calculate the MD5 hash of a file."""
       hash_md5 = hashlib.md5()
       with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
       return hash_md5.hexdigest()
    def client_receive_server_updates(self):
        if self.server_socket==None:
            print("A?")
            return
        while True:
            print("B???")
            operation_type_s=self.server_socket.recv(1024)
            print("C???")
            operation_type=pickle.loads(operation_type_s)
            if type(operation_type)!=type(0):
                continue
            print("o:"+str(operation_type))
            file_size_s=self.server_socket.recv(1024)
            file_size=pickle.loads(file_size_s)
            print("s"+str(file_size))
            file_name_s=self.server_socket.recv(1024)
            file_name=pickle.loads(file_name_s)
            print(file_name)
            f=open(file_name,'wb')
            current_size=0
            recv_len=1024
            while True:
               filedata=self.server_socket.recv(recv_len)
               current_size+=len(filedata)
               f.write(filedata)
               if current_size==int(file_size):
                   f.close()
                   break
               if current_size+recv_len>=int(file_size):
                   recv_len=file_size-current_size
                
    def start_file_monitor(self,directory_path, interval=0.5):
       current_list=os.listdir(directory_path)
       current_md5_list=[]
       for file in current_list:
          current_md5_list.append(self.calculate_md5("share/"+file))
       while True:
           time.sleep(2)
           new_list=os.listdir(directory_path)
           if len(new_list)==len(current_list):
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
               if len(new_list)<len(current_list):
                  for file_d in current_list:
                      if new_list.count(file_d)==0:
                          servernotifythread=threading.Thread(target=self.notify_server,args=("share/"+file_d,))
                          servernotifythread.start()
                          print("file changed B")
               else:
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
