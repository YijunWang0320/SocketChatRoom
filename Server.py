import socket
import sys
import select
import json
from collections import defaultdict
from datetime import datetime
from thread import *
import threading
from WatchDog import WatchDog

server = None

class Server(object):
    """The server Class"""

    def __init__(self, ip, port, heart_beat):
        super(Server, self).__init__()
        self.ip = ip
        self.port = port
        self.heart_beat = heart_beat
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_list = []
        self.user_info = defaultdict(dict)
        self.message_queue = defaultdict(list)
        self.block_queue = defaultdict(list)
        self.time_queue = dict()
        self.lock = threading.Lock()
        self.time_lock = threading.Lock()

    def loadup(self):
        """
        Currently, we put the cred file in the same folder as the server file
        We load the users and the passwords into the Server.
        """
        fp = open('credentials.txt')
        for line in fp:
            line = line.strip()
            str1 = line.split(' ')
            self.user_info[str1[0]]['password'] = str1[1]
            self.user_info[str1[0]]['status'] = 'logoff'
            self.block_queue[str1[0]] = list()
            self.message_queue[str1[0]] = list()
        fp.close()

    def conn_thread(self, sock):
        """
            It decides what the users is asking for and handle it with different functions.
        """
        try:
            data = json.loads(sock.recv(4096))
            assert type(data) is dict
            if data['type'] != 'login' and data['self'] in self.user_info.keys() and self.user_info[data['self']]['status'] != 'login':
                raise socket.error
            if data['type'] == 'login':
                self.login(data, sock)
            elif data['type'] == 'heartbeat':
                self.time_lock.acquire()
                self.time_queue[data['self']].reset()
                self.time_queue[data['self']].start()
                self.time_lock.release()
            elif data['type'] == 'offmsg':
                self.getoffmsg(data, sock)
            elif data['type'] == 'message':
                self.message(data, sock)
            elif data['type'] == 'broadcast':
                self.broadcast(data, sock)
            elif data['type'] == 'online':
                self.online(data, sock)
            elif data['type'] == 'block':
                self.block(data, sock)
            elif data['type'] == 'unblock':
                self.unblock(data, sock)
            elif data['type'] == 'logout':
                self.logout(data, sock)
            elif data['type'] == 'getaddress':
                self.getaddress(data, sock)
            else:
                print 'you might have a special way to get through the client, but the server does not support this command.'
        except socket.error:
            print 'Something wrong about the socket'
        finally:
            sock.close()

    def start(self):
        """
            This is the main function of the Server. It bind the socket with (ip, port) and start listening.
            For every incoming socket, it creates a new process for the socket.
        """
        try:
            self.server.bind((self.ip, self.port))
        except socket.error, e:
            print 'Bind failed, Error Code : ' + str(e[0]) + '  Message: ' + e[1]
            sys.exit()
        self.server.listen(20)
        self.connection_list.append(self.server)

        while True:
            read_sockets, write_sockets, error_sockets = select.select(self.connection_list, [], [])
            for sock in read_sockets:
                if sock == self.server:
                    sockfd, addr = self.server.accept()
                    self.connection_list.append(sockfd)
                else:
                    self.connection_list.remove(sock)
                    start_new_thread(self.conn_thread, (sock,))

    """
        This is a simple wrapper function to forward message, the socket in this function should be non-blocking/ muti-thread
    """
    def forward(self, forward_ip, data):
        forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            forward_socket.connect((forward_ip, 4009))
            forward_socket.sendall(json.dumps(data))
        except socket.error, msg:
            print 'Cannot connect to the user' + str(msg)
        finally:
            forward_socket.close()
        return

    def check_time(self, user_name):
        self.lock.acquire()
        self.user_info[user_name]['status'] = 'logoff'
        self.lock.release()
        return

    '''
        The function is used to login.
    '''
    def login(self, data, sock):
        """
        the login code here.
        we have a lock here, so we try not to put any blocking code in the lock
        all the blocking code are outside the lock
        """
        peername = sock.getpeername()
        self.lock.acquire()
        if data['username'] in self.user_info.keys() and data['password'] == self.user_info[data['username']]['password']:
            ret = {'message': 3}
            if 'lastAttempt' in self.user_info[data['username']].keys():
                self.user_info[data['username']]['time'] = 0
            if self.user_info[data['username']]['status'] == 'login':
                if self.user_info[data['username']]['ip'] != peername[0]:
                    tmp_ip = self.user_info[data['username']]['ip']
                    # this part could block, so release the lock first
                    self.lock.release()
                    self.forward(tmp_ip, {'type': 'force_logout', 'to': data['username']})
                    self.lock.acquire()
                else:
                    ret = {'message': 4}
            self.user_info[data['username']]['status'] = 'login'
            self.user_info[data['username']]['ip'] = peername[0]
        elif data['username'] not in self.user_info.keys():
            ret = {'message': 2}
        else:
            if 'lastAttempt' in self.user_info[data['username']].keys():
                if (datetime.now() - self.user_info[data['username']]['lastAttempt']).seconds < 60:
                    if self.user_info[data['username']]['time'] < 2:
                        self.user_info[data['username']]['time'] += 1
                        ret = {'message': 1, 'time': 3 - self.user_info[data['username']]['time']}
                    else:
                        ret = {'message': 0}
                else:
                    self.user_info[data['username']]['time'] = 1
                    ret = {'message': 1, 'time': 2}
                self.user_info[data['username']]['lastAttempt'] = datetime.now()
            else:
                self.user_info[data['username']]['lastAttempt'] = datetime.now()
                self.user_info[data['username']]['time'] = 1
                ret = {'message': 1, 'time': 2}
        self.lock.release()
        sock.sendall(json.dumps(ret))
        if ret['message'] == 3:
            watchDog = WatchDog(self.heart_beat, [data['username']], self.check_time)
            watchDog.start()
            self.time_lock.acquire()
            self.time_queue[data['username']] = watchDog
            self.time_lock.release()
            self.broadcast({'self': data['username'], 'message': data['username'] + ' is online.'}, None)
        return

    def getoffmsg(self, data, sock):
        retlist = []
        self.lock.acquire()
        if data['self'] not in self.user_info.keys():
            print 'something wrong, no such user'
        else:
            retlist = self.message_queue[data['self']]
            self.message_queue[data['self']] = []
        self.lock.release()
        sock.sendall(json.dumps(retlist))
        return

    def message(self, data, sock):
        """
            Here we have the code for message.
            Because the code is multi-threaded, for concurrency and consistency, we put all the shared objects in to the critical area protected by
            the lock, and put the blocking part (the socket) outside of the critical area.
        """
        ret = {'message': 0}
        self.lock.acquire()
        if data['user'] not in self.user_info.keys():
            ret = {'message': 3}
            self.lock.release()
        elif data['self'] in self.block_queue[data['user']]:
            ret = {'message': 2}
            self.lock.release()
        elif self.user_info[data['user']]['status'] == 'logoff':
            ret = {'message': 1}
            self.message_queue[data['user']].append(data['self'] + ': ' + data['message'])
            self.lock.release()
        else:
            info_tuple = (self.user_info[data['user']]['ip'], 4009)
            dict_message = {'user': data['self'], 'message': data['message'], 'to': data['user']}
            self.lock.release()
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                forward_socket.connect(info_tuple)
                forward_socket.sendall(json.dumps(dict_message))
            except socket.error, msg:
                ret = {'message': 3}
                print 'unable to send the message to the user, because ' + str(msg)
            finally:
                forward_socket.close()
        sock.sendall(json.dumps(ret))
        return

    def broadcast(self, data, sock):
        """
            We try to broadcast the message.
        """
        tmplist = list()
        self.lock.acquire()
        for name in self.user_info.keys():
            if self.user_info[name]['status'] == 'login' and data['self'] not in self.block_queue[name] and name != data['self']:
                tmplist.append((self.user_info[name]['ip'], name))
        self.lock.release()
        for t in tmplist:
            dict_message = {'user': data['self'], 'message': data['message'], 'to': t[1]}
            self.forward(t[0], dict_message)
        return

    def online(self, data, sock):
        """
            This currently returns all the users that is online (not including the ones that blocked the user)
        """
        tmplist = list()
        self.lock.acquire()
        for name in self.user_info.keys():
            if self.user_info[name]['status'] == 'login' and data['self'] not in self.block_queue[name]:
                tmplist.append(name)
        self.lock.release()
        sock.sendall(json.dumps(tmplist))
        return

    def block(self, data, sock):
        """
            This currently blocks one user
        """
        self.lock.acquire()
        if data['user'] not in self.user_info.keys():
            ret = {'message': 1}
        else:
            ret = {'message': 0}
            if data['user'] != data['self']:
                if data['user'] not in self.block_queue[data['self']]:
                    self.block_queue[data['self']].append(data['user'])
        self.lock.release()
        sock.sendall(json.dumps(ret))
        return

    def unblock(self, data, sock):
        """
            This unblocks one user
        """
        self.lock.acquire()
        if data['user'] not in self.user_info.keys():
            ret = {'message': 1}
        else:
            ret = {'message': 0}
            if data['user'] != data['self']:
                if data['user'] in self.block_queue[data['self']]:
                    self.block_queue[data['self']].remove(data['user'])
        self.lock.release()
        sock.sendall(json.dumps(ret))
        return

    def logout(self, data, sock):
        ret = {'message': 0}
        self.lock.acquire()
        self.user_info[data['self']]['status'] = 'logoff'
        self.lock.release()
        sock.sendall(json.dumps(ret))
        return

    def getaddress(self, data, sock):
        self.lock.acquire()
        if data['user'] not in self.user_info.keys():
            ret = {'message': 1}
        elif self.user_info[data['user']]['status'] == 'logoff':
            ret = {'message': 2}
        elif data['self'] in self.block_queue[data['user']]:
            ret = {'message': 3}
        else:
            ret = {'message': 0, 'ip': self.user_info[data['user']]['ip']}
        self.lock.release()
        sock.sendall(json.dumps(ret))
        return

def main():
    global server
    ip = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    PORT = 4009
    heart_beat = 30.0
    """
        read configuration file
    """
    fp = open('config.txt')
    for line in fp:
        line = line.strip()
        config = line.split('=')
        if len(config) != 2:
            continue
        if config[0] == 'HeartBeat' and int(config[1]) > 20:
            heart_beat = int(config[1])
        elif config[0] == 'PORT':
            PORT = int(config[1])
    fp.close()

    server = Server(ip, 4010, heart_beat)
    server.loadup()
    print 'Ready to start, the ip address is ' + ip + ' the port number is ' + str(PORT)
    print 'the heart beat time is 30s'
    server.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'sucessfully shut down server'
    except:
        print 'Unexpected error'
    finally:
        if server:
            server.server.close()
