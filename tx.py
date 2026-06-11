import cv2
import numpy as np
import socket
import time
import struct
import av  # pip install av

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_IP = "127.0.0.1"
UDP_PORT = 5000

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# H.264 encoder: low-latency + capped bitrate so I-frames stay small
encoder = av.CodecContext.create("libx264", "w")
encoder.width = 320
encoder.height = 240
encoder.pix_fmt = "yuv420p"
encoder.framerate = 15
encoder.bit_rate = 400000          # ~400 kbps cap, keeps packets under MTU
encoder.options = {
    "preset": "ultrafast",
    "tune": "zerolatency",
    "g": "30",                     # fewer (smaller load) keyframes
    "sliced-threads": "0",
}

MARKER = [255, 0, 254, 1]
frame_count = 0


def send_packet(payload, seq):
    seq_high = (seq >> 8) & 0xFF
    seq_low = seq & 0xFF
    # MARKER(4) + seq(2) + length(4) + payload
    header = bytearray(MARKER + [seq_high, seq_low]) + struct.pack(">I", len(payload))
    try:
        sock.sendto(header + payload, (UDP_IP, UDP_PORT))
    except Exception:
        pass


while True:
    time.sleep(0.05)

    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    av_frame = av.VideoFrame.from_ndarray(bgr, format="bgr24")
    for pkt in encoder.encode(av_frame):
        send_packet(bytes(pkt), frame_count % 65535)
        frame_count += 1

    cv2.imshow("TX Camera", gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

for pkt in encoder.encode(None):
    send_packet(bytes(pkt), 0)

cap.release()
cv2.destroyAllWindows()
