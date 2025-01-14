# Reliable-Data-Transfer-Protocol

This directory is designated for writing the solution code for Homework 5. No other files should be modified in this directory.

## Description

The provided solution code implements a reliable data transfer protocol in Python for a TCP-like communication system. It includes functionalities such as sequence number tracking, packet acknowledgment, and timeout handling with exponential weighted moving average (EWMA) for round-trip time (RTT) estimation.

## Solution Components

### `send` Function

The `send` function is responsible for sending data packets over a socket connection. It splits the data into packets of a specified size and sends them sequentially. It also handles packet acknowledgment and adjusts the timeout value based on the estimated RTT.

### `recv` Function

The `recv` function receives data packets from a socket connection and writes them to a destination buffer. It also sends acknowledgment packets for received packets, ensuring reliable data transfer. It adjusts the timeout value based on successful acknowledgments.

## Usage

To use the solution code, import the necessary functions into your Python script and call them with appropriate parameters.

```python
import socket
import io
import homework

# Create a socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8080))

# Send data
homework.send(sock, b'Hello, world!')

# Receive data
with open('output.txt', 'wb') as f:
    homework.recv(sock, f)

# Close the socket connection
sock.close()
