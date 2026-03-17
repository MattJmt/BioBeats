# PPG — Photoplethysmography Heart Rate

Real-time heartbeat detection from a photoplethysmography sensor connected to a SparkFun Pro Micro.

---

## Hardware

- Pro Micro (shared with piezo glove / EMG)
- Photodiode / PPG sensor on analog input
- USB serial connection to host

---

## Files

| File | Description |
|------|-------------|
| `ppg_raw/ppg_raw.ino` | Arduino firmware — reads analog sensor, outputs `t_ms,raw_value` at 115200 baud |
| `ppg_detect.py` | Beat detector — reads serial, applies baseline removal + smoothing, detects peaks |
| `ppg_viewer.py` | Live plot — launches `ppg_detect.py` as a subprocess and visualizes raw, filtered, and beat signals |

---

## Usage

### Visualize (recommended)

```bash
python3 ppg/ppg_viewer.py
```

Opens a 20-second rolling plot showing:
- Raw signal (blue)
- Baseline-removed + smoothed signal (orange)
- Pulse gate (green, scaled for visibility)
- Beat markers (red dots)

This internally runs `ppg_detect.py` — no need to start it separately.

### Headless / pipe output

```bash
python3 ppg/ppg_detect.py
```

Prints a CSV stream to stdout:

```
t_ms,raw,filtered,beat,pulse
```

- `beat` — 1 on the sample where a peak was detected, 0 otherwise
- `pulse` — 1 for 120 ms after each beat (gate signal, useful for triggering)

---

## Configuration

Edit the constants at the top of `ppg_detect.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `PORT` | `/dev/ttyACM0` | Serial port — update to match your system |
| `BAUD` | `115200` | Must match firmware |
| `THRESHOLD` | `4.0` | Minimum filtered amplitude to accept a peak |
| `REFRACTORY_MS` | `450` | Minimum gap between beats (~133 BPM max) |
| `PULSE_WIDTH_MS` | `120` | Duration of the pulse gate after each beat |
| `BASELINE_WINDOW` | `80` | Samples used for rolling baseline (~0.4 s at 200 Hz) |
| `SMOOTH_WINDOW` | `8` | Samples in the smoothing average |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `serial.SerialException` / port not found | Update `PORT` in `ppg_detect.py` — check `ls /dev/tty*` |
| No beats detected | Lower `THRESHOLD`; check sensor contact and ambient light |
| False beats / double-triggering | Raise `THRESHOLD` or `REFRACTORY_MS` |
| Plot is blank | Confirm firmware is flashed and serial data is flowing |
