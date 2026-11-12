# MULTITHREADED CACHING PROXY SERVER

## 1. Project Overview
The Multithreaded Caching Proxy Server is a Python-based networking project that handles multiple HTTP and HTTPS client requests using socket programming and multithreading.

## 2. Project Objectives
- Handle multiple client connections simultaneously.
- Parse raw HTTP requests.
- Support HTTPS CONNECT tunneling.
- Implement LRU cache eviction.
- Prevent race conditions using thread synchronization.

## 3. Technologies Used
- Python
- Socket Programming
- Threading
- SSL/TLS Concepts
- HTTP/HTTPS
- OrderedDict
- Thread Lock

## 4. Project Modules
- proxy_server.py: Main proxy server.
- http_handler.py: HTTP request parsing and HTTPS tunneling.
- cache.py: LRU cache implementation.
- config.py: Server configuration.
- README.md: Project documentation.

## 5. Working
The client sends a request to the proxy server. The server accepts the connection and assigns a separate thread to handle the client.

For HTTP GET requests, the proxy checks its cache. If the response exists, it returns cached data. Otherwise, it fetches the response from the destination server and stores eligible responses in the cache.

HTTPS connections are forwarded through a CONNECT tunnel.

## 6. LRU Cache
The Least Recently Used (LRU) algorithm removes the least recently accessed item when the cache reaches its capacity.

## 7. Race Condition Management
Threading Lock is used to protect shared cache operations and prevent simultaneous modifications.

## 8. Testing Results
- HTTP request testing: Successful
- HTTPS tunneling testing: Successful
- Cache MISS testing: Successful
- Cache HIT testing: Successful
- Parallel request testing: Successful

## 9. Conclusion
The project demonstrates socket programming, multithreading, HTTP/HTTPS communication, caching, LRU eviction and thread synchronization using Python.