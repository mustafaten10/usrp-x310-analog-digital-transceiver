import cv2
import numpy as np
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_IP = "127.0.0.1"
UDP_PORT = 5001
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.1)

MARKER = bytes([255, 0, 254, 1])
buffer = b""

while True:
    try:
        data, addr = sock.recvfrom(65535)
        buffer += data
    except socket.timeout:
        pass
        
    marker_start = buffer.find(MARKER)
    
    if marker_start != -1:
        next_marker = buffer.find(MARKER, marker_start + 6)
        
        if next_marker != -1:
            jpeg_data = buffer[marker_start + 6 : next_marker]
            
            seq_high = buffer[marker_start + 4]
            seq_low = buffer[marker_start + 5]
            seq_no = (seq_high << 8) | seq_low
            
            img_array = np.frombuffer(jpeg_data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
            
            if frame is not None:
                cv2.imshow("RX Video Stream", frame)
                
            buffer = buffer[next_marker:]
            
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()