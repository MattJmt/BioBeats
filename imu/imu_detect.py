import socket
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import threading

HOST = '127.0.0.1'
PORT = 8888
WINDOW = 200

data = [deque([0]*WINDOW, maxlen=WINDOW) for _ in range(12)]
imu_labels = [f"IMU{i}_{ax}" for i in range(4) for ax in ['X','Y','Z']]
colors = ['r', 'g', 'b']

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
f = sock.makefile()
print("Connected!")

def read_data():
    while True:
        try:
            line = f.readline().strip()
            if line:
                vals = list(map(int, line.split(',')))
                if len(vals) == 12:
                    for i, v in enumerate(vals):
                        data[i].append(v)
        except:
            pass

thread = threading.Thread(target=read_data, daemon=True)
thread.start()

fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
lines = []

for i, ax in enumerate(axes):
    for j in range(3):
        line, = ax.plot(range(WINDOW), list(data[i*3+j]),
                        color=colors[j], label=imu_labels[i*3+j])
        lines.append(line)
    ax.set_ylabel(f'IMU {i}')
    ax.legend(loc='upper right', fontsize=7)
    ax.set_ylim(-32768, 32768)
    ax.grid(True, alpha=0.3)

axes[-1].set_xlabel('Samples')
fig.suptitle('LSM6DSO32 - 4 IMUs Accelerometer', fontsize=12)
plt.tight_layout()

def update(frame):
    for i, ln in enumerate(lines):
        ln.set_ydata(list(data[i]))
    for ax in axes:
        ax.relim()
        ax.autoscale_view(scalex=False)
    return lines

ani = animation.FuncAnimation(fig, update, interval=50, blit=False, cache_frame_data=False)
plt.show()