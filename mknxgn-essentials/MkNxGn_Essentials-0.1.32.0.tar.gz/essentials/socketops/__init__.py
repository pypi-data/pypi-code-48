import struct, socket

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
        print("Connection Error!")

def SocketUpload(sock, data):
    try:
        data = pickle.dumps(data, 0)
        size = len(data)
        sock.sendall(struct.pack(">L", size) + data)
    except:
        print("Validation Failure. No Connection")

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
