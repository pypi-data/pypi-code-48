import struct, socket, threading, json
from essentials import tokening

def SocketDownload(sock):
    try:
        data = b""
        payload_size = struct.calcsize(">L")
        while True:
            while len(data) < payload_size:
                data += sock.recv(4096)
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            while len(data) < msg_size:
                data += sock.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            xData = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            return xData
    except:
        raise ConnectionError("Connection Error")

def SocketUpload(sock, data):
    try:
        data = pickle.dumps(data, 0)
        size = len(data)
        sock.sendall(struct.pack(">L", size) + data)
    except:
        raise ConnectionError("Connection Error")

def HostServer(HOST, PORT, connections=5):
    PORT = int(os.getenv('PORT', PORT))
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind((HOST,PORT))
    sock.listen(connections)
    return sock

def ConnectorSocket(HOST, PORT):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((HOST, PORT))
    return clientsocket


class Socket_Server_Host:

    def __init__(self, HOST, PORT, on_connection_open, on_data_recv, connections=5, on_connection_close=False):
        self.on_connection_open = on_connection_open
        self.on_connection_close = on_connection_close
        self.on_data_recv = on_data_recv
        self.HOST = HOST
        self.PORT = PORT
        self.connections = {}
        self.running = True
        self.server = HostServer(HOST, PORT, connections)
        self.broker = threading.Thread(target=self.ConnectionBroker, daemon=True)
        self.broker.start()

    def ConnectionBroker(self):
        while self.running:
            conn, addr = self.server.accept()
            conID = tokening.CreateToken(12, self.connections)
            self.connections[conID] = Socket_Server_Client(conn, addr, conID, self.on_data_recv, on_close=self.on_connection_close)
            self.on_connection_open(conID)

    def Shutdown(self):
        self.running = False
        for con in self.connections:
            self.connections[con].shutdown()
        self.connections = {}

    def CloseConnection(conID):
        self.connections[conID].shutdown()
        del self.connections[conID]

class Socket_Server_Client:

    def __init__(self, socket, addr, conID, on_data, on_close):
        self.socket = socket
        self.addr = addr
        self.conID = conID
        self.on_data = on_data
        self.on_close = on_close
        self.running = True
        self.data_Recv = threading.Thread(target=self.__data_rev__, daemon=True)
        self.data_Recv.start()

    def shutdown(self):
        self.running = False
        self.socket.shutdown()
        self.socket.close()

    def send(self, data, is_json=True):
        if is_json:
            data = json.dumps(data)
        try:
            SocketUpload(self.socket, data)
        except:
            self.shutdown()
            self.on_close()

    def __data_rev__(self):
        while self.running:
            data = SocketDownload(self.socket)
            try:
                data = json.loads(data)
            except:
                pass
            self.on_data(data, self)


class Socket_Connector:

    def __init__(self, HOST, PORT, on_data_recv):
        self.running = True
        self.HOST = HOST
        self.PORT = PORT
        self.on_data_recv = on_data_recv
        self.data_Recv = threading.Thread(target=self.__data_rev__, daemon=True)
        self.data_Recv.start()

    def send(self, data, is_json=True):
        if is_json:
            data = json.dumps(data)
        SocketUpload(self.socket, data)
    
    def __data_rev__(self):
        while self.running:
            data = SocketDownload(self.socket)
            try:
                data = json.loads(data)
            except:
                pass
            self.on_data(data)