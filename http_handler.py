
import socket
import select
from urllib.parse import urlsplit

from config import BUFFER_SIZE, CACHE_SIZE
from cache import LRUCache

cache = LRUCache(CACHE_SIZE)


def parse_request(data):
    try:
        text = data.decode("iso-8859-1")
        lines = text.split("\r\n")

        method, target, version = lines[0].split(" ", 2)

        headers = {}

        for line in lines[1:]:
            if not line:
                break

            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        return method.upper(), target, version, headers

    except (ValueError, IndexError):
        return None


def send_error(client, code, message):
    response = (
        f"HTTP/1.1 {code} {message}\r\n"
        "Connection: close\r\n"
        "Content-Length: 0\r\n\r\n"
    )
    client.sendall(response.encode())


def handle_http(client, data):

    parsed = parse_request(data)

    if parsed is None:
        send_error(client, 400, "Bad Request")
        return

    method, target, version, headers = parsed

    if method == "CONNECT":
        handle_https(client, target)
        return

    if method != "GET":
        send_error(client, 501, "Not Implemented")
        return

    host = headers.get("host")

    if not host:
        send_error(client, 400, "Missing Host")
        return

    if any(c in host for c in "\r\n/@\\"):
        send_error(client, 400, "Invalid Host")
        return

    try:
        if target.startswith("http://"):
            parts = urlsplit(target)
        else:
            parts = urlsplit("//" + host)

        hostname = parts.hostname
        port = parts.port or 80

        if not hostname or not 1 <= port <= 65535:
            raise ValueError()

        if target.startswith("http://"):
            host_parts = urlsplit("//" + host)

            if host_parts.hostname != hostname:
                raise ValueError()

            path = parts.path or "/"

            if parts.query:
                path += "?" + parts.query
        else:
            path = target

        if not path.startswith("/") or any(
            c in path for c in "\r\n"
        ):
            raise ValueError()

    except ValueError:
        send_error(client, 400, "Invalid Request")
        return

    key = f"{hostname}:{port}{path}"

    cached_response = cache.get(key)

    if cached_response is not None:
        print("Cache HIT:", key)
        client.sendall(cached_response)
        return

    print("Cache MISS:", key)

    request = (
        f"GET {path} {version}\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n\r\n"
    )

    try:
        with socket.create_connection(
            (hostname, port), timeout=15
        ) as remote:

            remote.sendall(
                request.encode("iso-8859-1")
            )

            remote.settimeout(15)

            response_parts = []

            while True:
                chunk = remote.recv(BUFFER_SIZE)

                if not chunk:
                    break

                response_parts.append(chunk)

        response = b"".join(response_parts)

        if not response:
            send_error(client, 502, "Empty Response")
            return

        if response.startswith(b"HTTP/1.1 200"):
            cache.put(key, response)

        client.sendall(response)

    except OSError as error:
        print("HTTP Error:", error)
        send_error(client, 502, "Bad Gateway")


def handle_https(client, target):

    try:
        host, port = target.rsplit(":", 1)
        port = int(port)

        if not host or port != 443:
            raise ValueError()

        if any(c in host for c in "\r\n/@\\"):
            raise ValueError()

        with socket.create_connection(
            (host, port), timeout=15
        ) as remote:

            client.sendall(
                b"HTTP/1.1 200 Connection Established\r\n\r\n"
            )

            client.settimeout(30)
            remote.settimeout(30)

            while True:

                ready, _, _ = select.select(
                    [client, remote], [], [], 30
                )

                if not ready:
                    break

                for source in ready:

                    destination = (
                        remote if source is client else client
                    )

                    chunk = source.recv(BUFFER_SIZE)

                    if not chunk:
                        return

                    destination.sendall(chunk)

    except (OSError, ValueError) as error:
        print("HTTPS Error:", error)

        try:
            send_error(client, 502, "Bad Gateway")
        except OSError:
            pass