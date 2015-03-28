author: Yijun Wang
        yw2676@columbia.edu

If there is some major problem, please contact me. I've done the test on a slightly different environment than the Clic Machines. Thank you.

1. Description:
    5 py files are included: Server.py, Client.py, CommandLine.py, Parser.py, WatchDog.py
    3 files are included: README.txt, config.txt, credentials.txt

    Server.py: This is where the main Server code lies. It handles different commands that comes from the client.

    Client.py: This is a little special. To handle the situation where two or more users are logged on from one computer (which have the same ip address).
               Since the different users logged on from one computer would have the same ip address and port number (I assume that we are asked to use only 4009),
               I used this client to deliver message to different users. (A user has 3 labels: ip, port, username)

    CommandLine.py: This is used as a actually client, Client.py should be seen as a protocol.

    Parser.py: It is used to parse input and output.

    WatchDog.py: To allow the server and client receive and send out heart beat message. It is implemented using a timer.

    README.txt: Documentation

    config.txt: The configuration file. The IP address and the port number of the Server, and the heart beat interval.
                The form is HOST=129.236.213.247
                            PORT=4009
                            HeartBeat=30
                Currently, the format have to be same as above, the only thing that need to change is on the right side of '=', no space is allowed

    credentials.txt: The usernames and the passwords. It is assumed that all the users are friends at first, you could block others later.

2. DataStructures:
    (a) Because we do not need to persist the data, so most of the data are save in the dictionary.
    (b) Lists are used to keep the sockets.
    (c) The protocol message should be designed as a class, but currently I uses the dictionary to pass the messages.

3. Explanation of the code:
    The code is commented, so please have a look.

4. How to run the code?
    First, put Server.py, Watchdog.py, credentials.txt, config.txt on the server side under the same folder.
    And then, put Client.py, CommandLine.py, Parser.py, WatchDog.py, config.txt on the client side under the same folder.

    Second, run the Server on the server side:
        python Server.py

    Third, run the Client (the protocol) on the client side:
        python Client.py

    At last, run the CommandLine tool, make sure the Client.py is running before opening CommandLine tool:
        python CommandLine.py

    This is the process of running the code.

5. The sample process:

    1. start the server:
        Ready to start, the ip address is 129.236.213.247 the port number is 4010
        the heart beat time is 30s

    2. start the client:
    3. start one CommandLine:
    Columbia:
>Username:
columbia
>Password:
116bway
>you have successfully logged in to the Chat Server!
>cur
No such command
>message windows a
message sent out successfully
>online
columbia
>getaddress windows
The user is offline, there is no valid ip address
>windows: windows is online.
>windows: hi
>getaddress windows
The ip address of the user is 129.236.213.247
>private windows hi
Message send out successfully
>windows: goodbye
>logout
>logout successfully

(This user is logged out using logout command)

    Windows:
>Username:
windows
>Password:
withglass
>you have successfully logged in to the Chat Server!
>columbia: a
>message columbia hi
message sent out successfully
>columbia: hi
>message columbia goodbye
message sent out successfully
>Exit the program

(This user is logged out using ctrl+c)


6. What can be improved?

   (a) Multi-threading or non-blocking:
       At first, I did not know the asyncore class, so I used the socket class and used multi-threading.
       Though the process, I think non-blocking is easier and better way too develop a chat server.

   (b) The protocol
       I should have a wrapper class like java bean to pack the protocol details. Currently, I only use the json dictionaries to pass the messages
       between the Server and Clients. The code looks a little messy this way.

   (c) Some synchronization issues:
       At first there are no bugs in the program. After I add the multi-threading property, the synchronization and sequence of execution becomes a issue.
       I fixed most of them, but there might be other underlying bugs that I did not find out.

