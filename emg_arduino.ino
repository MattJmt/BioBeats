/*
  EMG RMS reader with manual calibration
  - RMS printed every loop
  - Normalized control printed at 20 Hz
  - Keeps the same delay(10) sampling as the simple script
*/

const int EMG_PIN = A0;

const int WINDOW = 40;
const int OUTPUT_INTERVAL_MS = 50;  // 20 Hz control signal

// Manual calibration values
const float EMG_MIN = 5.5;
const float EMG_MAX = 12.0;

int buffer[WINDOW];
int index = 0;
long sumSquares = 0;

unsigned long lastOutputTime = 0;

void setup() {
  Serial.begin(115200);
}

void loop() {

  int raw = analogRead(EMG_PIN);

  // remove oldest sample
  sumSquares -= buffer[index];

  // add newest squared sample
  int squared = raw * raw;
  buffer[index] = squared;
  sumSquares += squared;

  index++;
  if (index >= WINDOW) index = 0;

  // compute RMS
  float rms = sqrt((float)sumSquares / WINDOW);

  // print RMS every loop (for calibration/plotting)
  // Serial.print("RMS:");
  // Serial.println(rms, 3);

  // print normalized control at lower frequency
  unsigned long now = millis();
  if (now - lastOutputTime >= OUTPUT_INTERVAL_MS) {

    lastOutputTime = now;

    float normalized = (rms - EMG_MIN) / (EMG_MAX - EMG_MIN);

    if (normalized < 0.0) normalized = 0.0;
    if (normalized > 1.0) normalized = 1.0;

    // Serial.print("CTRL:");
    Serial.println(normalized, 3);
  }

  // keep same sampling as earlier script
  delay(10);
}