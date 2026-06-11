import cv2
import numpy as np
import socket
import struct
import av  # pip install av

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_IP = "127.0.0.1"
UDP_PORT = 5001
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.1)

decoder = av.CodecContext.create("h264", "r")

MARKER = bytes([255, 0, 254, 1])
HEADER_LEN = 10  # MARKER(4) + seq(2) + length(4)
buffer = b""

while True:
    try:
        data, addr = sock.recvfrom(65535)
        buffer += data
    except socket.timeout:
        pass

    # Process every complete packet currently in the buffer (no waiting for next marker)
    while True:
        marker_start = buffer.find(MARKER)
        if marker_start == -1 or len(buffer) < marker_start + HEADER_LEN:
            break

        length = struct.unpack(">I", buffer[marker_start + 6 : marker_start + 10])[0]
        end = marker_start + HEADER_LEN + length
        if len(buffer) < end:
            break  # full payload not arrived yet

        h264_data = buffer[marker_start + HEADER_LEN : end]
        buffer = buffer[end:]

        try:
            pkt = av.Packet(h264_data)
            for av_frame in decoder.decode(pkt):
                frame = av_frame.to_ndarray(format="bgr24")
                cv2.imshow("RX Video Stream", frame)
        except Exception:
            pass

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
