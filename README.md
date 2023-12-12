# Large File Sharing System
## Prerequisite
To run the project, You need at least three virtual machines requested.
## How to Run
#### for start node 
`python3 main.py`
#### for normal node 
`python3 client.py server_ip server_port client_ip client_port`

 * Here server_ip and server_port means the ip and the port of the server, client_ip and client_port means the ip and the port this client should bind to after you have start all.
 * You can add, delete, modify any file under /share in normal node. Your change will be sychronized on all normal nodes or  we can say client nodes.
 * The typical file size suggested for testing for this project is <=10MB.
## Demo Video
https://www.flexclip.com/share/4705506b725d2823449a0ed5e20862b8f376399.html
   
   
