import sys
import socket
import pickle
import threading
import server_connection
import client_p2p_connection
import os
# prepare for final merge
class Server:
    # Class variable
    client_nodes=[]
    client_nodes_address=[]
    server_socket=None
    # Constructor (initializer) method
    def __init__(self, client_nodes=[]):
        # Instance variables
        self.client_nodes=client_nodes
        self.processed_array = []
    # Instance method
    def init_socket(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('67.159.89.70', 12345)  # may need change
        server_socket.bind(server_address)
        server_socket.listen(1000)
        self.server_socket=server_socket
        return server_socket
    def get_connections(self):
        print(self.client_nodes)
        return self.client_nodes
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
                    try:
                      print("start success!!!!!!")
                      def client_handler(server_socket,client_socket):
                        try:
                         server_connection.handle_client(server_socket,client_socket)
                        except:
                         self.client_nodes.remove(self.client_nodes.index(client_socket))
                      for myclient in self.client_nodes:
                        if self.processed_array.count(myclient)==0:
                            clienthandler = threading.Thread(target=client_handler, args=(self, myclient))
                            clienthandler.start()
                            self.processed_array.append(myclient)
                    except:
                       server_socket.close()
    
    

# socket_array = []
# processed_array=[]

# def handle_connection(server_socket):
#     client_socket_dic = []  # record ip and port only,through recv from client,which is ip port
#     lock = threading.Lock()
#     while True:
#         print("Waiting for a connection...")
#         client_socket, client_address = server_socket.accept()
#         socket_array.append(client_socket)  # remeber all the socket
#         client_info_str = client_socket.recv(1024)
#         print(client_info_str)
#         client_info_str = pickle.loads(client_info_str)
#         client_info_list = client_info_str.split(" ")
#         client_ip = client_info_list[0]
#         client_port = int(client_info_list[1])
#         client_socket_dic.append([client_ip, client_port])
#         with lock:
#                     for socket in socket_array:
#                         socket.send(pickle.dumps(client_socket_dic))
#                     try:
#                       print("start success!!!!!!")
#                       def client_handler(server_socket,client_socket):
#                         try:
#                          server_connection.handle_client(server_socket,client_socket)
#                         except:
#                          socket_array.remove(socket_array.index(client_socket))
#                       for myclient in socket_array:
#                         if processed_array.count(myclient)==0:
#                             clienthandler = threading.Thread(target=client_handler, args=(server_socket, myclient))
#                             clienthandler.start()
#                             processed_array.append(myclient)
#                     except:
#                        server_socket.close()

# def get_connections():
#     print("The socket array is ")
#     print(socket_array)
#     return socket_array

if __name__ == '__main__':
    # socket_array = []
    # processed_array=[]
    if len(sys.argv) == 1:  # The code for server side

        # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_address = ('67.159.89.70', 12345)  # may need change
        # server_socket.bind(server_address)
        # server_socket.listen(1000)
        # connectionhandler = threading.Thread(target=handle_connection,args=(server_socket,))
        # connectionhandler.start()
        thisserver=Server()
        thread1=threading.Thread(target=thisserver.init_connections)
        thread1.start()
    else:
        if len(sys.argv) < 5:
            print("wrong format!")
            exit(0)
        #  client side logic
        # Define the directory name
        dir_name = "share"

        # Get the current working directory
        current_dir = os.getcwd()

        # Create the full path for the "share" directory
        share_dir = os.path.join(current_dir, dir_name)

        # Check if the "share" directory exists
        if os.path.exists(share_dir):
            # If it exists, clear all files inside it
            for filename in os.listdir(share_dir):
                file_path = os.path.join(share_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error: {e}")
        else:
            # If it doesn't exist, create an empty "share" directory
            os.makedirs(share_dir)

        print(f"{dir_name} directory is now ready.")
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        client_entry_thread = threading.Thread(target=client_p2p_connection.client_entry,
                                               args=((server_ip, server_port, sys.argv[3], int(sys.argv[4]))))
        client_entry_thread.start()