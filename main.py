import socket
import threading
import re

server = "irc.libera.chat"
port = 6667
channel = "###test"  # Default channel
nickname = "Testaccount"

if nickname.startswith("$") or nickname.startswith(":"):
    print(
        """
    Nicknames are non-empty strings with the following restrictions:
    They MUST NOT contain any of the following characters: space (' ', 0x20), comma (',', 0x2C), asterisk ('*', 0x2A), question mark ('?', 0x3F), exclamation mark ('!', 0x21), at sign ('@', 0x40).
    They MUST NOT start with any of the following characters: dollar ('$', 0x24), colon (':', 0x3A).")
    """
    )
    exit()


def send_message(sock, channel, message):
    sock.send(f"PRIVMSG {channel} :{message}\r\n".encode())


def receive_messages(sock):
    while True:
        data = sock.recv(4096).decode().strip("\n\r")
        # Clean the message
        data = re.sub(r"[\x02\x1f\x1d\x1e]", "", data)
        # Extract the sender's name and message content
        match = re.match(r":(\S+)!\S+ PRIVMSG (\S+) :(.*)", data)
        if match:
            sender = match.group(1)
            message = match.group(3)
            print(f"{sender}: {message}")
        elif "353" in data:  # NAMES response
            names = data.split(":")[-1].strip("\n\r").split()
            print(f"Users in {channel}: {', '.join(names)}")


def main():
    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_socket.connect((server, port))
    irc_socket.send(f"USER {nickname} {nickname} {nickname} :{nickname}\r\n".encode())
    print (f"Connected to {server} on port {port}")
    irc_socket.send(f"NICK {nickname}\r\n".encode())
    print(f"Nickname set to {nickname}")
    irc_socket.send(f"JOIN {channel}\r\n".encode())
    print(f"Joined channel {channel}")

    send_thread = threading.Thread(target=send_loop, args=(irc_socket,))
    receive_thread = threading.Thread(target=receive_messages, args=(irc_socket,))

    send_thread.start()
    receive_thread.start()

def send_loop(sock):
    global channel
    while True:
        message = input()
        if message == "/exit":
            break
        elif message.startswith("/join"):
            new_channel = message.split(" ")[1]
            sock.send(f"JOIN {new_channel}\r\n".encode())
            channel = new_channel  
        elif message.startswith("/msg"):
            recipient = message.split(" ")[1]
            message = " ".join(message.split(" ")[2:])
            send_message(sock, recipient, message)
        elif message == "/NAMES":
            sock.send(f"NAMES {channel}\r\n".encode())
        else:
            send_message(sock, channel, message)

    sock.close()


if __name__ == "__main__":
    main()
