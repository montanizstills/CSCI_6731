import queue
import random
import socket as mySock
import threading

from cryptography.fernet import Fernet


def udp_client_2(key):
    # Create a UDP socket for the client
    client = mySock.socket(mySock.AF_INET, mySock.SOCK_DGRAM)

    # Bind the client to a random port in the range 8000-9000
    client.bind(("localhost", random.randint(8000, 9000)))

    # Function to receive messages from the server
    def receive():
        while True:
            try:
                # Receive a message from the server
                message, server_address = client.recvfrom(1024)
                encrypted_byte_str = message.decode()[2:-1]

                print(decrypt(key, encrypted_byte_str.encode()))



            except:
                pass

    # Create a thread for receiving messages
    t = threading.Thread(target=receive)
    t.start()

    # Main loop for sending messages to the server
    while True:
        # Get user input for a message
        message = input("")

        # Check if the user wants to quit
        if message == "!q":
            exit()
        else:
            # Send the user's message to the server
            encrypted_message = encrypt(key, message)
            client.sendto(f"{encrypted_message}".encode(), ("localhost", 9999))


def upd_server_2():
    # Initialize a queue to store client messages
    messages = queue.Queue()

    # List to track connected clients
    clients = []

    # Create a UDP socket for the server
    server = mySock.socket(mySock.AF_INET, mySock.SOCK_DGRAM)

    # Bind the server to the specified address and port
    server.bind(("localhost", 9999))

    key = generate_key()

    # Function to handle incoming messages from clients
    def receive():
        while True:  # Continuously listen for messages
            try:
                # Receive a message and the sender's address
                message, addr = server.recvfrom(1024)

                # Add the message and address to the queue
                messages.put((message, addr))
            except:
                pass

    # Function to broadcast messages to all connected clients
    def broadcast():
        while True:
            # Check if there are messages in the queue
            while not messages.empty():
                # Get the message and sender's address from the queue
                message, addr = messages.get()

                # Decode and display the message
                print(f"{message.decode()}")

                # If the client is new, add them to the clients list
                if addr not in clients:
                    clients.append(addr)

                # Send the message to all connected clients
                for client in clients:
                    try:
                        server.sendto(message, client)
                    except:
                        # Remove unreachable clients
                        clients.remove(client)

    # Start threads for receiving and broadcasting messages
    t1 = threading.Thread(target=receive)
    t2 = threading.Thread(target=broadcast)

    t1.start()  # Start the receiver thread
    t2.start()  # Start the broadcaster thread

    return key.decode()


def generate_key():
    return Fernet.generate_key()


def decrypt(key, encrypted_bytes):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_bytes)
    return decrypted_message.decode()


def encrypt(key, text):
    f = Fernet(key.encode())
    encrypted_byte_message = f.encrypt(text.encode())
    return encrypted_byte_message

