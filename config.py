# config.py
# Pin mapping (ubah sesuai wiring kamu)
PIN_TRIG = 5
PIN_ECHO = 18
PIN_IR   = 19
PIN_MOTOR = 23
PIN_BUZZER = 25

# Sensor settings
ULTRA_TIMEOUT_US = 30000        # 30 ms timeout (~5m max)
SAMPLE_MS = 80                  # loop interval (ms)

# Filtering
WINDOW = 5                      # sliding window size
OUTLIER_JUMP_CM = 80            # kalau loncat jarak ekstrim -> anggap noise

# Adaptive threshold settings
THRESH_SLOW = 80                # cm (jalan pelan / kondisi ramai -> threshold lebih kecil)
THRESH_FAST = 140               # cm (jalan cepat -> threshold lebih besar)
SPEED_FAST_SCORE = 18           # skor gerak, semakin kecil semakin sensitif "fast"
SPEED_SLOW_SCORE = 8

# Output (haptic)
MIN_DUTY = 200                  # PWM duty untuk motor (0-1023)
MAX_DUTY = 900
BEEP_FREQ = 1200
