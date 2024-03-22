import socket
import threading
import re
import os

server = "irc.libera.chat"
port = 6667
channel = "###test"
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


def send_message(sock, message):
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
    global channel  # Declare channel as a global variable
    while True:
        message = input()
        try: 
            if message == "/exit":
                break
            elif message == "/list":
                sock.send(f"LIST\r\n".encode())
                print(sock.recv(4096).decode("utf-8", errors="ignore"))
            elif message.startswith("/join"):
                channel = message.split(" ")[1]
                sock.send(f"JOIN {channel}\r\n".encode())
                sock.send(f"NAMES {channel}\r\n".encode())
                sock.send(f"WHO {channel}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/cls"):
                print("\n" * 100)
                os.system("cls" if os.name == "nt" else "clear")
            elif message == "/Names":
                sock.send(f"NAMES {channel}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/msg"):
                parts = message.split(" ", 2)
                recipient = parts[1]
                message_content = parts[2]
                sock.send(f"PRIVMSG {recipient} :{message_content}\r\n".encode())
            elif message.startswith("/nick"):
                new_nickname = message.split(" ")[1]
                sock.send(f"NICK {new_nickname}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/quit"):
                quit_message = " ".join(message.split(" ")[1:])
                sock.send(f"QUIT :{quit_message}\r\n".encode())
                print(sock.recv(4096).decode())
                break
            elif message.startswith("/whois"):
                target_user = message.split(" ")[1]
                sock.send(f"WHOIS {target_user}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/away"):
                away_message = " ".join(message.split(" ")[1:])
                sock.send(f"AWAY :{away_message}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/topic"):
                parts = message.split(" ", 2)
                channel = parts[1]
                new_topic = parts[2] if len(parts) > 2 else None
                if new_topic:
                    sock.send(f"TOPIC {channel} :{new_topic}\r\n".encode())
                else:
                    sock.send(f"TOPIC {channel}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/kick"):
                parts = message.split(" ", 3)
                channel = parts[1]
                user = parts[2]
                reason = parts[3] if len(parts) > 3 else None
                if reason:
                    sock.send(f"KICK {channel} {user} :{reason}\r\n".encode())
                else:
                    sock.send(f"KICK {channel} {user}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/invite"):
                parts = message.split(" ", 2)
                user = parts[1]
                channel = parts[2]
                sock.send(f"INVITE {user} {channel}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/mode"):
                parts = message.split(" ", 2)
                channel = parts[1]
                mode = parts[2]
                sock.send(f"MODE {channel} {mode}\r\n".encode())
                print(sock.recv(4096).decode())
            elif message.startswith("/me"):
                action = message.split(" ", 1)[1]
                sock.send(f"PRIVMSG {channel} :\x01ACTION {action}\x01\r\n".encode())
                print(sock.recv(4096).decode())
            elif message == "/help":
                print("Available commands:")
                print("/list - List all channels")
                print("/join <channel> - Join a channel")
                print("/cls - Clear the screen")
                print("/Names - List users in the current channel")
                print("/msg <user> <message> - Send a private message")
                print("/nick <nickname> - Change your nickname")
                print("/quit [<reason>] - Quit from the server")
                print("/whois <user> - Get information about a user")
                print("/away [<message>] - Set an away message")
                print(
                    "/topic [<channel>] [<new_topic>] - Set or display the topic of a channel"
                )
                print("/kick <channel> <user> [<reason>] - Kick a user from a channel")
                print("/invite <user> <channel> - Invite a user to a channel")
                print("/mode <channel> <mode> - Set or display channel modes")
                print("/me <action> - Perform an action in the channel")
            else:
                send_message(sock, message)
        except Exception as e:
            print(f"An error occurred: {e}")

    sock.close()


if __name__ == "__main__":
    main()
