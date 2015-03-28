import socket
import sys
import json
import select
import os
from thread import *
import threading

client = None

class Client(object):
    """ The Client Class, this could be seen as a protocol, with out this class, we cannot have multiple users on one (client, port)"""

    def __init__(self, ip, port):
        super(Client, self).__init__()
        self.ip = ip
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commandline = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connection_list = []
        self.lock = threading.Lock()
        """
            This data structure is used to keep track of the users logged in on this client. (With same (ip, port))
        """
        self.client_list = dict()

    def start(self):
        """
            There are two sockets listening to connections.
            One is for the incoming server sockets looking to send in messages. (No permanent connection)
            Another is for the incoming CommandLine sockets looking to send out messages. (Permanent connection, it's like a port)
        """
        my_name = socket.getfqdn(socket.gethostname())
        HOST = socket.gethostbyname(my_name)
        PORT = 4009
        # this is for the commandLine connections
        conn = './client'

        print HOST
        try:
            self.client.bind((HOST, PORT))
            if os.path.exists(conn):
                os.unlink(conn)
            self.commandline.bind(conn)
        except socket.error, msg:
            print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
            sys.exit()
        self.client.listen(10)
        self.commandline.listen(10)
        self.connection_list.append(self.client)
        self.connection_list.append(self.commandline)

    def connect(self, data):
        # data = {'type': 'login', 'username': username, 'password': password}
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_socket.settimeout(6)
        try:
            send_socket.connect((self.ip, self.port))
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        try:
            send_socket.sendall(json.dumps(data))
            result = send_socket.recv(4096)
            return result
        except socket.error, msg:
            print 'unable to sendout' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def disconnect(self, data):
        # data = {'type': 'logout', 'username': self.username}
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.sendall(json.dumps(data))
            result = send_socket.recv(4096)
            if not result:
                result = {'message': -1}
            else:
                result = json.loads(result)
            return result
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def message(self, data):
        # data = {'type': 'message', 'user': user, 'message': message, 'self': self.username}
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_socket.settimeout(6)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.sendall(json.dumps(data))
            result = send_socket.recv(4096)
            if not result:
                result = {'message': -1}
            else:
                result = json.loads(result)
            return result
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def broadcast(self, data):
        # data = {'type': 'broadcast', 'message': message, 'self': self.username}
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.send(json.dumps(data))
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def online(self, data):
        # data = {'type': 'online', 'self': self.username}
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.sendall(json.dumps(data))
            result = send_socket.recv(4096)
            if not result:
                result = {'message': -1}
            else:
                result = json.loads(result)
            return result
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def send_heartbeat(self, data):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.send(json.dumps(data))
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def block(self, data):
        # data = {'type': 'block', 'user': user, 'self': self.username}
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.sendall(json.dumps(data))
            result = send_socket.recv(4096)
            if not result:
                result = {'message': -1}
            else:
                result = json.loads(result)
            return result
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def unblock(self, data):
        # data = {'type': 'unblock', 'user': user, 'self': self.username}
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.sendall(json.dumps(data))
            result = send_socket.recv(4096)
            if not result:
                result = {'message': -1}
            else:
                result = json.loads(result)
            return result
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def getaddress(self, data):
        # data = {'type': 'getaddress', 'user': user, 'self': self.username}
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.sendall(json.dumps(data))
            result = send_socket.recv(4096)
            if not result:
                result = {'message': -1}
            else:
                result = json.loads(result)
            return result
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

    def private(self, data):
        # we send this to users directly, do something later
        forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            dict_message = {'user': data['self'], 'message': data['message'], 'to': data['user'], 'type': 'private'}
            forward_socket.connect((data['ip'], 4009))
            forward_socket.sendall(json.dumps(dict_message))
            ret = json.loads(forward_socket.recv(4096))
        except socket.error, msg:
            ret = {'message': -1}
            print str(msg[0]) + msg[1]
        finally:
            forward_socket.close()
        return ret

    def getoffmsg(self, data):
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            send_socket.connect((self.ip, self.port))
            send_socket.sendall(json.dumps(data))
            result = send_socket.recv(4096)
            if not result:
                result = {'message': -1}
            else:
                result = json.loads(result)
            return result
        except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
        finally:
            send_socket.close()

"""
    The data format is mainly as follows. Maybe creating a class for this would be a improvement.

    data:
        from: user
        self: username
        type: logout, message...
        user: to whom?
        // password for connection

    data:
        from: server
        self: from whom
        type: what kind of information
        user: to whom?

"""


def server_socket(data, sock):
    """
        Handling the sockets coming from the server, trying to sending in the messages.
    """
    global client
    client.lock.acquire()
    if data['to'] in client.client_list.keys():
        client.lock.release()
        ret = {'message': 1}
    else:
        client.lock.release()
        ret = {'message': -1}
    """
        We first give the response because there is a situation that we use private my_self.
        We have to keep the sequence right.
    """
    if 'type' in data.keys() and data['type'] == 'private':
        sock.sendall(json.dumps(ret))
    client.lock.acquire()
    if data['to'] in client.client_list.keys():
        client.lock.release()
        sockfd = client.client_list[data['to']]
        sockfd.sendall(json.dumps(data))
    else:
        client.lock.release()
    return


def user_socket(data, sock):
    """
        Handles the sockets coming from the users, sending out messages.
    """
    global client
    if data['type'] == 'login':
        ret = json.loads(client.connect(data))
        if ret['message'] == 3:
            client.client_list[data['username']] = sock
        sock.sendall(json.dumps(ret))
    elif data['type'] == 'heartbeat':
        client.send_heartbeat(data)
    elif data['type'] == 'offmsg':
        ret = client.getoffmsg(data)
        sock.sendall(json.dumps(ret))
    elif data['type'] == 'logout':
        ret = client.disconnect(data)
        sock.sendall(json.dumps(ret))
        if ret['message'] == 0:
            client.lock.acquire()
            client.client_list.pop(data['self'], None)
            client.lock.release()
    elif data['type'] == 'message':
        ret = client.message(data)
        sock.sendall(json.dumps(ret))
    elif data['type'] == 'broadcast':
        client.broadcast(data)
    elif data['type'] == 'online':
        ret = client.online(data)
        sock.sendall(json.dumps(ret))
    elif data['type'] == 'block':
        ret = client.block(data)
        sock.sendall(json.dumps(ret))
    elif data['type'] == 'unblock':
        ret = client.unblock(data)
        sock.sendall(json.dumps(ret))
    elif data['type'] == 'getaddress':
        ret = client.getaddress(data)
        sock.sendall(json.dumps(ret))
    elif data['type'] == 'private':
        ret = client.private(data)
        sock.sendall(json.dumps(ret))
    else:
        pass
    return


def main():
    global client
    HOST = ''
    PORT = 4009

    """
        Reading the configuration file.
    """
    fp = open('config.txt')
    for line in fp:
        line = line.strip()
        config = line.split('=')
        if len(config) != 2:
            continue
        if config[0] == 'HOST':
            HOST = config[1]
        elif config[0] == 'PORT':
            PORT = int(config[1])
        else:
            pass
    fp.close()

    client = Client(HOST, PORT)
    client.start()
    while True:
        """
            Listening to the sockets.
        """
        read_sockets, write_sockets, error_sockets = select.select(client.connection_list, [], [])
        for sock in read_sockets:
            if sock is client.client:
                sockfd, address = sock.accept()
                client.lock.acquire()
                client.connection_list.append(sockfd)
                client.lock.release()
            elif sock is client.commandline:
                sockfd, address = sock.accept()
                client.lock.acquire()
                client.connection_list.append(sockfd)
                client.lock.release()
            else:
                data = sock.recv(4096)
                if not data:
                    client.lock.acquire()
                    if sock in client.connection_list:
                        client.connection_list.remove(sock)
                    sock.close()
                    client.lock.release()
                    continue
                else:
                    data = json.loads(data)
                assert type(data) is dict
                if 'from' in data.keys() and data['from'] == 'user':
                    """
                        Sockets from the users, use user_socket function to handle it.
                    """
                    start_new_thread(user_socket, (data, sock))
                else:
                    """
                        Sockets from the server, user server_socket function to handle it.
                    """
                    start_new_thread(server_socket, (data, sock))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'successfully shut down the clients'
    except:
        print 'Unexpected Error'
