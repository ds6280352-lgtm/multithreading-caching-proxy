import socket
import threading

from config import HOST, PORT, BUFFER_SIZE
from http_handler import handle_http


total_requests = 0
active_clients = 0
server_running = False
server_error = None

stats_lock = threading.Lock()


def get_server_stats():
    with stats_lock:
        return {
            "total_requests": total_requests,
            "active_clients": active_clients,
            "running": server_running,
            "error": server_error
        }


def handle_client(client_socket, address):
    global active_clients

    print("Client Connected:", address)

    try:
        data = client_socket.recv(BUFFER_SIZE)

        if data:
            handle_http(client_socket, data)

    except Exception as error:
        print("Client Error:", error)

    finally:
        try:
            client_socket.close()
        except OSError:
            pass

        with stats_lock:
            active_clients -= 1

        print("Client Disconnected:", address)


def start_server():
    global total_requests, active_clients
    global server_running, server_error

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(20)
        server_socket.settimeout(1)

        with stats_lock:
            server_running = True
            server_error = None

        print("Proxy Server Started")
        print("Listening on:", HOST, PORT)

        while True:
            try:
                client_socket, address = server_socket.accept()

            except socket.timeout:
                continue

            with stats_lock:
                total_requests += 1
                active_clients += 1

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )

            client_thread.start()

    except Exception as error:
        with stats_lock:
            server_error = str(error)
            server_running = False

        print("Proxy Server Error:", error)

    finally:
        with stats_lock:
            server_running = False

        server_socket.close()