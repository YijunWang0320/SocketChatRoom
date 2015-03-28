

class Parser(object):
    """
        The class that can do all the parsing job
        It takes the command line input and parse it into variables that the client need.
    """
    def __init__(self):
        super(Parser, self).__init__()

    def parse(self, command):
        assert type(command) is str
        words = command.strip().split(' ')
        if len(words) == 0:
            return 0, 0, 0
        elif words[0] == 'message':
            if len(words) < 3:
                return -1, 0, 0
            else:
                temp = ''
                for i in range(2, len(words)):
                    temp += words[i] + ' '
                return 1, words[1], temp
        elif words[0] == 'broadcast':
            if len(words) < 2:
                return -1, 0, 0
            else:
                temp = ''
                for i in range(1, len(words)):
                    temp += words[i] + ' '
                return 2, temp, 0
        elif words[0] == 'online':
            if len(words) != 1:
                return -1, 0, 0
            else:
                return 3, 0, 0
        elif words[0] == 'block':
            if len(words) != 2:
                return -1, 0, 0
            else:
                return 4, words[1], 0
        elif words[0] == 'unblock':
            if len(words) != 2:
                return -1, 0, 0
            else:
                return 5, words[1], 0
        elif words[0] == 'logout':
            if len(words) != 1:
                return -1, 0, 0
            else:
                return 6, 0, 0
        elif words[0] == 'getaddress':
            if len(words) != 2:
                return -1, 0, 0
            else:
                return 7, words[1], 0
        elif words[0] == 'private':
            if len(words) != 3:
                return -1, 0, 0
            else:
                return 8, words[1], words[2]
        else:
            return -2, 0, 0

    def getOutput(self, data):
        assert type(data) is dict
        return data['user'], data['message']