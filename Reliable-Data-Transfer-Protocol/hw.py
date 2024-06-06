"""
Where solution code to HW5 should be written.  No other files should
be modified.
"""

import socket
import io
import time
import typing
import struct
import homework
import homework.logging


PACKET_SIZE = homework.MAX_PACKET
HEADER_SIZE = 4  # Assume a 4-byte header for sequence numbers
ALPHA = 0.125  # Alpha value for EWMA
estimated_rtt = 0.1  # Initial estimated RTT (in seconds)
TIMEOUT = estimated_rtt  # Initial timeout value

def send(sock: socket.socket, data: bytes):
    logger = homework.logging.get_logger("hw-tcp-sender")
    seq_number = 0
    global TIMEOUT  # Declare TIMEOUT as global to modify its value
    while seq_number * PACKET_SIZE < len(data):
        # Prepare packet
        payload = data[seq_number * PACKET_SIZE:(seq_number + 1) * PACKET_SIZE]
        packet = struct.pack(f'I{len(payload)}s', seq_number, payload)
        
        # Send packet
        sock.send(packet)
        logger.info("Sent packet with sequence number %d", seq_number)

        # Wait for acknowledgment
        try:
            sock.settimeout(TIMEOUT)
            start_time = time.time()
            ack = struct.unpack('I', sock.recv(HEADER_SIZE))[0]
            end_time = time.time()
            
            # Calculate Sample RTT
            sample_rtt = end_time - start_time
            
            # Update Estimated RTT using EWMA formula
            global estimated_rtt
            estimated_rtt = (1 - ALPHA) * estimated_rtt + ALPHA * sample_rtt
            
            if ack == seq_number:
                seq_number += 1
                TIMEOUT = estimated_rtt + 4 * estimated_rtt  # Update timeout for successful transmission
            else:
                TIMEOUT *= 1.1  # Update timeout for failed transmission
        except socket.timeout:
            logger.error("Timeout occurred, resending packet with sequence number %d", seq_number)
            TIMEOUT *= 1.5  # Increase timeout for retransmission

def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    logger = homework.logging.get_logger("hw-tcp-receiver")
    expected_seq_number = 0
    num_bytes = 0
    global TIMEOUT  # Declare TIMEOUT as global to modify its value
    while True:
        try:
            sock.settimeout(TIMEOUT)
            packet = sock.recv(PACKET_SIZE + HEADER_SIZE)
            seq_number, payload = struct.unpack(f'I{len(packet) - HEADER_SIZE}s', packet)
            
            # Send acknowledgment
            ack_packet = struct.pack('I', seq_number)
            sock.send(ack_packet)
            
            if seq_number == expected_seq_number:
                dest.write(payload)
                num_bytes += len(payload)
                expected_seq_number += 1
            TIMEOUT *= 0.9  # Update timeout for successful acknowledgment
        except socket.timeout:
            logger.error("Timeout occurred, expected sequence number %d", expected_seq_number)
            TIMEOUT *= 1.5  # Increase timeout for retransmission
            continue  # Continue loop to handle retransmission
            
        if len(payload) < PACKET_SIZE:
            break  # End of transmission
    return num_bytes
