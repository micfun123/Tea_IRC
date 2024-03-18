import socket
import threading
import re
import os

server = "irc.libera.chat"
port = 6667
channel = "###test"
nickname = "Testaccount"

if nickname.startswith('$') or nickname.startswith(':'):
    print("""
    Nicknames are non-empty strings with the following restrictions:
    They MUST NOT contain any of the following characters: space (' ', 0x20), comma (',', 0x2C), asterisk ('*', 0x2A), question mark ('?', 0x3F), exclamation mark ('!', 0x21), at sign ('@', 0x40).
    They MUST NOT start with any of the following characters: dollar ('$', 0x24), colon (':', 0x3A).")
    """)
    exit()

          
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
        elif message.startswith("/cls"):
            print("\n" * 100)
            os.system('cls' if os.name == 'nt' else 'clear')
        elif message == "/here":
            sock.send(f"NAMES {channel}\r\n".encode())
        elif message == "/help":
            print("""
            /exit - exit the chat
            /list - list all channels
            /join <channel> - join a channel
            /cls - clear the screen
            /here - list all users in the channel
            /help - list all commands
            """)
        else:
            send_message(sock, message)
            
    sock.close()



if __name__ == "__main__":
    main()
