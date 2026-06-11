import cv2
import numpy as np
import socket
import time  # Bunu ekledik

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_IP = "127.0.0.1"
UDP_PORT = 5000

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

MARKER = [255, 0, 254, 1]
frame_count = 0

while True:
    # Sistemi rahatlatmak ve FPS'i ~10-15 civarında tutmak için ufak bir bekleme
    time.sleep(0.05) 
    
    ret, frame = cap.read()
    if not ret: break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Kaliteyi 40'tan 20'ye düşürdük. Hareket anındaki veri patlamasını önler.
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20] 
    result, encimg = cv2.imencode('.jpg', gray, encode_param)
    
    seq_high = ((frame_count % 65535) >> 8) & 0xFF
    seq_low = (frame_count % 65535) & 0xFF
    header = bytearray(MARKER + [seq_high, seq_low])
    
    packet = header + encimg.tobytes()

    try:
        sock.sendto(packet, (UDP_IP, UDP_PORT))
    except Exception as e:
        pass
        
    frame_count += 1
    
    cv2.imshow("TX Camera", gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()