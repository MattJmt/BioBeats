import socket
from collections import deque
import threading
import time
import numpy as np
from pythonosc import udp_client

HOST = '127.0.0.1'
PORT = 8888

GRAVITY_ALPHA = 0.98
TAP_THRESHOLD = [5000, 5000, 4500, 4000]  # per-IMU (index=thumb, middle, ring, pinky-side)
TAP_COOLDOWN_SAMPLES = 5   # samples to ignore after a tap (per-IMU)
TAP_GLOBAL_LOCKOUT = 0     # samples all other IMUs are suppressed after any tap

# --- OSC UDP output ---
TARGET_IP  = "10.29.145.118"  # replace with receiver's IP
UDP_PORT   = 9000
osc_client = udp_client.SimpleUDPClient(TARGET_IP, UDP_PORT)

# --- Sample rate estimation ---
packet_times = deque(maxlen=200)
sample_rate_est = 0.0

# --- Global lockout ---
global_lockout = 0

# --- Terminal tap display: counts down per IMU after a tap fires ---
tap_flash = [0] * 4

# --- Per-IMU state ---
class IMUState:
    def __init__(self):
        self.gravity = np.zeros(3)
        self.baseline_samples = deque(maxlen=50)
        self.baseline_ready = False
        self.cooldown = 0

states = [IMUState() for _ in range(4)]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
f = sock.makefile()

def detect_tap(imu_idx, ax, ay, az):
    global global_lockout, tap_flash
    s = states[imu_idx]
    raw = np.array([float(ax), float(ay), float(az)])

    if not s.baseline_ready:
        s.baseline_samples.append(raw)
        if len(s.baseline_samples) == 50:
            s.gravity = np.mean(s.baseline_samples, axis=0)
            s.baseline_ready = True
        return

    s.gravity = GRAVITY_ALPHA * s.gravity + (1 - GRAVITY_ALPHA) * raw

    dynamic = raw - s.gravity
    gravity_norm = np.linalg.norm(s.gravity)
    proj = float(np.dot(dynamic, s.gravity / gravity_norm)) if gravity_norm > 0 else 0.0

    if s.cooldown > 0:
        s.cooldown -= 1
        return

    if global_lockout > 0:
        global_lockout -= 1
        return

    if proj < -TAP_THRESHOLD[imu_idx]:
        s.cooldown = TAP_COOLDOWN_SAMPLES
        global_lockout = TAP_GLOBAL_LOCKOUT
        msg = [1 if i == imu_idx else 0 for i in range(4)]
        osc_client.send_message('/taps', msg)
        tap_flash[imu_idx] = TAP_COOLDOWN_SAMPLES

def read_data():
    global sample_rate_est
    while True:
        try:
            line = f.readline().strip()
            if line:
                vals = list(map(int, line.split(',')))
                if len(vals) == 12:
                    now = time.time()
                    packet_times.append(now)
                    if len(packet_times) >= 10:
                        elapsed = packet_times[-1] - packet_times[0]
                        if elapsed > 0:
                            sample_rate_est = (len(packet_times) - 1) / elapsed
                    for i in range(4):
                        detect_tap(i, vals[i*3], vals[i*3+1], vals[i*3+2])
                    display = ''.join(str(1 if tap_flash[i] > 0 else 0) for i in range(4))
                    print(f"\r{display}", end='', flush=True)
                    for i in range(4):
                        if tap_flash[i] > 0:
                            tap_flash[i] -= 1
        except Exception:
            pass

thread = threading.Thread(target=read_data, daemon=True)
thread.start()
thread.join()
