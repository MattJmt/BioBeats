# EMG — Electromyography Muscle Activation

Single-channel EMG via a MyoWare muscle sensor → SparkFun Pro Micro. Outputs normalized muscle activation (0.0–1.0) over OSC.

---

## Files

| File | Description |
|------|-------------|
| `emg_arduino.ino` | Arduino firmware — RMS calculation on A0, outputs normalized float at 20 Hz |
| `emg_udp.py` | Bridge — reads serial, sends OSC `/emg` over UDP |

---

## Usage

1. Flash `emg_arduino.ino` to the Pro Micro via Arduino IDE
2. Run the bridge:

```bash
python3 emg/emg_udp.py
```

Sends OSC `/emg` (float 0.0–1.0) to `127.0.0.1:8001`.

---

## Configuration

Edit the constants at the top of each file:

**`emg_arduino.ino`**

| Constant | Default | Description |
|----------|---------|-------------|
| `EMG_MIN` | `5.5` | RMS value corresponding to 0.0 output — calibrate at rest |
| `EMG_MAX` | `12.0` | RMS value corresponding to 1.0 output — calibrate at full flex |
| `WINDOW` | `40` | RMS sliding window size (40 samples × 10 ms = 400 ms) |
| `OUTPUT_INTERVAL_MS` | `50` | Output rate (20 Hz) |

**`emg_udp.py`**

| Constant | Default | Description |
|----------|---------|-------------|
| `SERIAL_PORT` | `/dev/ttyACM0` | Update to match your system (macOS: `/dev/cu.usbserial-*`, Windows: `COM3`) |
| `TARGET_IP` | `127.0.0.1` | OSC target — change if Max is on a different machine |
| `UDP_PORT` | `8001` | OSC target port |

---

## Calibration

The firmware maps a raw RMS range to 0.0–1.0. To recalibrate:

1. Uncomment the `Serial.print("RMS:...")` line in `emg_arduino.ino`
2. Open Serial Monitor at 115200 baud
3. Note the RMS at rest → set `EMG_MIN`
4. Note the RMS at full muscle flex → set `EMG_MAX`
5. Re-comment the debug line and reflash
