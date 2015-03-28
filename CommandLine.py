import sys
import select
import json
import socket
from Parser import Parser
from WatchDog import WatchDog


client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
watchDog = None
address_list = dict()
my_username = None


def check_time(user_name):
    global watchDog
    data = {'from': 'user', 'type': 'heartbeat', 'self': user_name}
    client_socket.sendall(json.dumps(data))
    watchDog.reset()
    watchDog.start()
    return


def main():
    global watchDog
    global client_socket
    global address_list
    global my_username
    flag = True
    conn = './client'
    my_username = ''
    heart_beat = 20.0
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
            heart_beat = int(config[1]) - 10
    fp.close()

    connection_list = list()
    connection_list.append(client_socket)
    try:
        client_socket.connect(conn)
    except socket.error, msg:
            print 'unable to connect' + str(msg[0]) + ' ' + msg[1]
            sys.exit()
    parser = Parser()
    while True:
        """
            Currently, we do not support \t\n\r in username and password, so foobar is equal to foo\tbar

            result == 4:
                The same user is running on the same client. You can log on from another client or change a username
                If the same user is logged on from <another IP>, the former user would be notified and automatically log out.
            result == 3:
                successfully login in
            result == 2,1:
                login unsuccessful
            result == 0:
                sorry, 3 times, you have to wait for 60 seconds

        """
        print '>Username:'
        username = sys.stdin.readline().strip('\t\n\r')
        print '>Password:'
        password = sys.stdin.readline().strip('\t\n\r')
        try:
            data = {'from': 'user', 'type': 'login', 'username': username, 'password': password}
            my_username = username
            client_socket.sendall(json.dumps(data))
            result = json.loads(client_socket.recv(4096))
        except:
            continue
        assert type(result) is dict
        if result['message'] == 3:
            break
        elif result['message'] == 4:
            print 'The user is logged in on the same client'
        elif result['message'] == 2:
            print 'sorry, your username is incorrect.'
        elif result['message'] == 1:
            print 'sorry, your password is incorrect, you have ' + str(result['time']) + ' left.'
        else:
            print 'sorry, you have input the wrong login message for 3 times, please wait for 60 seconds'

    print '>you have successfully logged in to the Chat Server!'

    """
        The setting of the watchDog.
    """

    watchDog = WatchDog(heart_beat, [my_username], check_time)
    watchDog.start()

    """
        Ask the Server to send all the offline message to me.
    """

    client_socket.sendall(json.dumps({'from': 'user', 'type': 'offmsg', 'self': my_username}))
    val = json.loads(client_socket.recv(4096))
    # print out the list on the screen
    assert type(val) is list
    for item in val:
        print '>' + item
    connection_list.append(sys.stdin)
    sys.stdout.write('>')
    while True:
        """
            Listen to the socket actions.
        """
        read_sockets, write_sockets, error_sockets = select.select(connection_list, [], [])
        for sock in read_sockets:
            if sock is sys.stdin:
                """
                    This is from the user input. After parsing, different input number means different command.
                """
                line = sys.stdin.readline()
                if not line:
                    continue
                result = parser.parse(line)
                if result[0] == -2:
                    print 'No such command'
                elif result[0] == -1:
                    print 'argument number not correct'
                elif result[0] == 0:
                    print ''
                elif result[0] == 1:
                    data = {'from': 'user', 'type': 'message', 'user': result[1], 'message': result[2], 'self': my_username}
                    client_socket.sendall(json.dumps(data))
                    ret = json.loads(client_socket.recv(4096))
                    assert type(ret) is dict
                    if ret['message'] == -1:
                        print 'Your are currently in a logged out situation, please log in again'
                        flag = False
                        break
                    elif ret['message'] == 0 or ret['message'] == 1:
                        """
                            we count in the mail box as successful
                        """
                        print 'message sent out successfully'
                    elif ret['message'] == 2:
                        print 'that user blocked you'
                    else:
                        print 'no user with that kind of username, please check again'
                elif result[0] == 2:
                    data = {'from': 'user', 'type': 'broadcast', 'message': result[1], 'self': my_username}
                    client_socket.sendall(json.dumps(data))
                elif result[0] == 3:
                    data = {'from': 'user', 'type': 'online', 'self': my_username}
                    client_socket.sendall(json.dumps(data))
                    online_list = json.loads(client_socket.recv(4096))
                    if type(online_list) is dict:
                        print 'Your are currently in a logged out situation, please log in again'
                        flag = False
                        break
                    for name in online_list:
                        sys.stdout.write(name + '\n')
                elif result[0] == 4:
                    data = {'from': 'user', 'type': 'block', 'user': result[1], 'self': my_username}
                    client_socket.sendall(json.dumps(data))
                    ret = json.loads(client_socket.recv(4096))
                    if ret['message'] == -1:
                        print 'Your are currently in a logged out situation, please log in again'
                        flag = False
                        break
                    elif ret['message'] == 0:
                        print 'block successful'
                    else:
                        print 'there is no user with that username'
                elif result[0] == 5:
                    data = {'from': 'user', 'type': 'unblock', 'user': result[1], 'self': my_username}
                    client_socket.sendall(json.dumps(data))
                    ret = json.loads(client_socket.recv(4096))
                    if ret['message'] == -1:
                        print 'Your are currently in a logged out situation, please log in again'
                        flag = False
                        break
                    elif ret['message'] == 0:
                        print 'unblock successful'
                    else:
                        print 'there is no user with that username'
                elif result[0] == 6:
                    data = {'from': 'user', 'type': 'logout', 'self': my_username}
                    client_socket.sendall(json.dumps(data))
                    ret = json.loads(client_socket.recv(4096))
                    if ret['message'] == -1:
                        print 'Your are currently in a logged out situation, please log in again'
                        flag = False
                        break
                    elif ret['message'] == 0:
                        flag = False
                        break
                    else:
                        print 'Did not logout successfully! Please try again!'
                elif result[0] == 7:
                    data = {'from': 'user', 'type': 'getaddress', 'user': result[1], 'self': my_username}
                    client_socket.sendall(json.dumps(data))
                    ret = json.loads(client_socket.recv(4096))
                    if ret['message'] == -1:
                        print 'Your are currently in a logged out situation, please log in again'
                        flag = False
                        break
                    elif ret['message'] == 1:
                        print 'There is no user with that username'
                    elif ret['message'] == 2:
                        print 'The user is offline, there is no valid ip address'
                    elif ret['message'] == 3:
                        print 'The user has already blocked you'
                    else:
                        print 'The ip address of the user is ' + ret['ip']
                        address_list[result[1]] = ret['ip']
                elif result[0] == 8:
                    # ret = client.private(client.getaddress(result[1]), result[2])
                    if result[1] not in address_list.keys():
                        print 'You do not have the users\' ip address or the user does not exist'
                    elif result[1] == my_username:
                        print 'Don\'t send the message to yourself'
                    else:
                        data = {'from': 'user', 'user': result[1], 'type': 'private', 'message': result[2], 'ip': address_list[result[1]], 'self': my_username}
                        client_socket.sendall(json.dumps(data))
                        ret = json.loads(client_socket.recv(4096))
                        if ret['message'] == 0:
                            print 'Your are currently in a logged out situation, please log in again'
                            flag = False
                            break
                        elif ret['message'] == -1:
                            print 'The user is not their anymore'
                        else:
                            print 'Message send out successfully'
                else:
                    print 'There must be something wrong since there is no such parameter!'
                sys.stdout.write('>')
            else:
                """
                    The message is from the Server, not user input.
                    Handle the input and display it.
                """
                finalData = json.loads(sock.recv(4096))
                if 'type' in finalData.keys() and finalData['type'] == 'force_logout':
                    print 'Some one logged in using this account from another IP'
                    flag = False
                else:
                    user, message = parser.getOutput(finalData)
                    sys.stdout.write(user + ': ' + message + '\n')
                    sys.stdout.write('>')
        if not flag:
            break
    print '>logout successfully'


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exit the program'
        """
            just add this part, this is for ctrl + c logout
        """
        data = {'from': 'user', 'type': 'logout', 'self': my_username}
        client_socket.sendall(json.dumps(data))
        json.loads(client_socket.recv(4096))
    except:
        print 'Unexpected Error'
    finally:
        if watchDog:
            watchDog.stop()
        if client_socket:
            client_socket.close()

