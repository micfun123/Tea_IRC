import socket
import threading
import re

server = "irc.libera.chat"
port = 6667
channel = "###test"
nickname = "Carrots"

def send_message(sock, message):
    sock.send(f"PRIVMSG {channel} :{message}\r\n".encode())

def receive_messages(sock):
    while True:
        data = sock.recv(4096).decode()
        data = data.strip("\n\r")
        #clean the message
        data = re.sub(r"\x02|\x1f|\x1d|\x1e", "", data)
        #remove the hostname from the message
        data = re.sub(r":.*?!", "", data)
        #remove the nickname from the message
        data = re.sub(r"Carrots", "", data)
        print(data)



def main():
    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_socket.connect((server, port))
    irc_socket.send(f"USER {nickname} {nickname} {nickname} :{nickname}\r\n".encode())
    irc_socket.send(f"NICK {nickname}\r\n".encode())
    irc_socket.send(f"JOIN {channel}\r\n".encode())

    send_thread = threading.Thread(target=send_loop, args=(irc_socket,))
    receive_thread = threading.Thread(target=receive_messages, args=(irc_socket,))

    send_thread.start()
    receive_thread.start()

def send_loop(sock):
    while True:
        message = input()
        if message == "/exit":
            break
        elif message == "/list":
            sock.send(f"LIST\r\n".encode())
        elif message.startswith("/join"):
            channel = message.split(" ")[1]
            sock.send(f"JOIN {channel}\r\n".encode())
            sock.send(f"NAMES {channel}\r\n".encode())
            sock.send(f"WHO {channel}\r\n".encode())
        else:
            send_message(sock, message)
            
    sock.close()



if __name__ == "__main__":
    main()
