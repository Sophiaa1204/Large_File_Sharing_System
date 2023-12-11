import pickle
import threading
import socket
import os
import time
class Server:
    # Class variable
    client_nodes=[]
    client_nodes_address=[]
    # Constructor (initializer) method
    def __init__(self, client_nodes=[]):
        # Instance variables
        self.client_nodes=client_nodes
    # Instance method
    def init_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('152.3.65.150', 12345)  # may need change
        server_socket.bind(server_address)
        server_socket.listen(1000)
        return server_socket
    def init_connections(self):
        server_socket=self.init_socket()
        while True:
                print("Waiting for a connection...")
                client_socket, client_address = server_socket.accept()
                self.client_nodes.append(client_socket)  # remeber all the socket
                client_info_str = client_socket.recv(1024)
                print(client_info_str)
                client_info_str = pickle.loads(client_info_str)
                client_info_list = client_info_str.split(" ")
                client_ip = client_info_list[0]
                client_port = int(client_info_list[1])
                self.client_nodes_address.append([client_ip, client_port])
                for socket in self.client_nodes:
                        socket.send(pickle.dumps(self.client_nodes_address))
    def notify_client_nodes(self,file_path,thisclient):
      if os.path.exists(file_path):
       for node in self.client_nodes:
           if node!=thisclient:
               node.send(pickle.dumps(0))
               file_size = os.path.getsize(file_path)
               node.send(pickle.dumps(file_size))
               print("size: " + str(file_size))
               node.send(pickle.dumps(file_path))

             # Read and send the file data in 1024-byte chunks
               all_length=0
               with open(file_path, 'rb') as file:
                chunk_size = 1024
                while True:
                 chunk = file.read(chunk_size)
                 node.send(chunk)
                 all_length+=len(chunk)
                 if all_length>=file_size:
                    break
      else:
       for node in self.client_nodes:
           if node!=thisclient:
            node.send(pickle.dumps(1))
            file_size =0
            node.send(pickle.dumps(file_size))
            node.send(pickle.dumps(file_path))
    def server_recv_file_client(self,client_socket):
         print("file recv hello!!!!!!!!!!!!!")
         while True:
              operationtypeserialized=client_socket.recv(1024)
              operationtype=0
              try:
                 operationtype=pickle.loads(operationtypeserialized)
              except:
                   continue
              print("aaaaaaa")
              print(operationtype)
              print("aaaaaaa")
              if operationtype==0:
                   filesizesd=client_socket.recv(1024)
                   filesize=pickle.loads(filesizesd)
                   print("bbbbbbbbb")
                   print(filesize)
                   print("bbbbbbbbbb")
                   filenamesd=client_socket.recv(1024)
                   print(filenamesd)
                   filename=pickle.loads(filenamesd)
                   print("ccccccccccc")
                   print(filename)
                   print("ccccccccccc")
                   f=open(filename,'wb')
                   current_len=0
                   recv_len=1096
                   while True:
                        filedata=client_socket.recv(recv_len)
                        f.write(filedata)
                        current_len+=len(filedata)
                        print(current_len)
                        if current_len>=filesize:
                             f.close()
                             serversendthread=threading.Thread(target=self.notify_client_nodes,args=(filename,client_socket,))
                             serversendthread.start()
                             break
                        else:
                             if current_len+recv_len>=filesize:
                                  recv_len=filesize-current_len
              else:
                  if operationtype==1:
                        filesizesd=client_socket.recv(1024)
                        filesize=pickle.loads(filesizesd)
                        filenamesd=client_socket.recv(1024)
                        filename=pickle.loads(filenamesd)
                        serversendthread=threading.Thread(target=self.notify_client_nodes,args=(filename,client_socket,))
                        serversendthread.start()
                        os.remove(filename)
    def server_recv_file(self):
       current_length=0
       processed_nodes=[]
       while True:
          time.sleep(1)
          if len(self.client_nodes)!=current_length and current_length!=0:
            for client in self.client_nodes:
              if processed_nodes.count(client)==0:
                   threadhere=threading.Thread(target=self.server_recv_file_client,args=(client,))
                   threadhere.start()
                   processed_nodes.append(client)
          else:
              if current_length==0:
                    for client in self.client_nodes:
                     if processed_nodes.count(client)==0:
                          threadhere=threading.Thread(target=self.server_recv_file_client,args=(client,))
                          threadhere.start()
                          processed_nodes.append(client)
          current_length=len(self.client_nodes)
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
thisserver=Server()
thread1=threading.Thread(target=thisserver.init_connections)
thread1.start()
print("after init!!!!!!!!!!!!!!!")
thread2=threading.Thread(target=thisserver.server_recv_file)
thread2.start() #server recv file