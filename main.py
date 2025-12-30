# main.py (MicroPython ESP32)
from machine import Pin, PWM, time_pulse_us
import time

try:
    import config
except ImportError:
    # fallback default jika config.py tidak ada
    class config:
        PIN_TRIG = 5
        PIN_ECHO = 18
        PIN_IR = 19
        PIN_MOTOR = 23
        PIN_BUZZER = 25
        ULTRA_TIMEOUT_US = 30000
        SAMPLE_MS = 80
        WINDOW = 5
        OUTLIER_JUMP_CM = 80
        THRESH_SLOW = 80
        THRESH_FAST = 140
        SPEED_FAST_SCORE = 18
        SPEED_SLOW_SCORE = 8
        MIN_DUTY = 200
        MAX_DUTY = 900
        BEEP_FREQ = 1200

# ---------- Utils: Sliding Window + Median ----------
class RingWindow:
    def __init__(self, n):
        self.n = n
        self.buf = []
    def add(self, x):
        self.buf.append(x)
        if len(self.buf) > self.n:
            self.buf.pop(0)
    def median(self):
        if not self.buf:
            return None
        s = sorted(self.buf)
        mid = len(s)//2
        return s[mid] if len(s) % 2 else (s[mid-1] + s[mid]) / 2
    def mean(self):
        if not self.buf:
            return None
        return sum(self.buf)/len(self.buf)
    def size(self):
        return len(self.buf)

# ---------- Sensor: Ultrasonic ----------
class Ultrasonic:
    def __init__(self, trig_pin, echo_pin, timeout_us=30000):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.timeout_us = timeout_us
        self.trig.value(0)

    def read_cm(self):
        # Trigger pulse 10us
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)

        dur = time_pulse_us(self.echo, 1, self.timeout_us)  # microseconds
        if dur < 0:
            return None
        # speed of sound ~0.0343 cm/us
        return (dur * 0.0343) / 2

# ---------- Sensor: IR Obstacle ----------
class IRObstacle:
    # Banyak modul IR: output LOW saat ada objek
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN)
    def detected(self):
        return self.pin.value() == 0

# ---------- Output: Motor + Buzzer ----------
class HapticBuzzer:
    def __init__(self, motor_pin, buzzer_pin):
        # motor pakai PWM biar bisa bertingkat
        self.motor_pwm = PWM(Pin(motor_pin), freq=180)  # motor low freq OK
        self.buzzer = PWM(Pin(buzzer_pin), freq=config.BEEP_FREQ)
        self.off()

    def off(self):
        self.motor_pwm.duty(0)
        self.buzzer.duty(0)

    def vibrate_level(self, duty):
        duty = max(0, min(1023, int(duty)))
        self.motor_pwm.duty(duty)

    def beep(self, on):
        if on:
            self.buzzer.freq(config.BEEP_FREQ)
            self.buzzer.duty(350)
        else:
            self.buzzer.duty(0)

# ---------- Adaptive Threshold (simple motion score) ----------
class MotionEstimator:
    """
    Tanpa MPU6050 pun bisa bikin 'pseudo speed' dari perubahan jarak.
    Semakin sering jarak berubah banyak => dianggap pengguna bergerak cepat / lingkungan dinamis.
    """
    def __init__(self):
        self.last = None
        self.score = 0  # 0..~30

    def update(self, dist_cm):
        if dist_cm is None:
            self.score = max(0, self.score - 1)
            return self.score

        if self.last is None:
            self.last = dist_cm
            return self.score

        delta = abs(dist_cm - self.last)
        self.last = dist_cm

        # delta besar => score naik
        if delta > 12:
            self.score = min(30, self.score + 2)
        elif delta > 5:
            self.score = min(30, self.score + 1)
        else:
            self.score = max(0, self.score - 1)

        return self.score

    def threshold_cm(self):
        # Score tinggi -> anggap "fast" -> threshold lebih besar
        if self.score >= config.SPEED_FAST_SCORE:
            return config.THRESH_FAST
        if self.score <= config.SPEED_SLOW_SCORE:
            return config.THRESH_SLOW
        # linear interpolate
        t = (self.score - config.SPEED_SLOW_SCORE) / (config.SPEED_FAST_SCORE - config.SPEED_SLOW_SCORE)
        return config.THRESH_SLOW + t * (config.THRESH_FAST - config.THRESH_SLOW)

# ---------- Main Logic ----------
ultra = Ultrasonic(config.PIN_TRIG, config.PIN_ECHO, config.ULTRA_TIMEOUT_US)
ir = IRObstacle(config.PIN_IR)
out = HapticBuzzer(config.PIN_MOTOR, config.PIN_BUZZER)

win = RingWindow(config.WINDOW)
motion = MotionEstimator()

last_valid = None

def is_outlier(new_cm, prev_cm):
    if new_cm is None or prev_cm is None:
        return False
    return abs(new_cm - prev_cm) > config.OUTLIER_JUMP_CM

def map_distance_to_duty(dist_cm, thr_cm):
    """
    dist kecil -> duty besar.
    0..thr => MAX..MIN
    """
    if dist_cm <= 0:
        return config.MAX_DUTY
    if dist_cm >= thr_cm:
        return 0
    # normalize
    x = 1 - (dist_cm / thr_cm)  # 0..1
    return config.MIN_DUTY + x * (config.MAX_DUTY - config.MIN_DUTY)

print("Smart Cane started (MicroPython ESP32)")
out.off()

while True:
    d = ultra.read_cm()

    # Anti noise: reject outlier jump
    if is_outlier(d, last_valid):
        # ignore reading
        d_used = last_valid
    else:
        d_used = d
        if d is not None:
            last_valid = d

    # filter window
    if d_used is not None:
        win.add(d_used)

    d_f = win.median() if win.size() >= 3 else d_used  # median lebih tahan noise
    score = motion.update(d_f)
    thr = motion.threshold_cm()

    ir_hit = ir.detected()

    # Sensor fusion rule:
    # - IR hit => selalu bahaya dekat (override)
    # - Ultrasonic median < threshold => bahaya
    danger = False
    if ir_hit:
        danger = True
    elif d_f is not None and d_f < thr:
        danger = True

    # Output policy
    if danger:
        # duty berdasarkan jarak; kalau IR hit tapi ultra none, kasih duty tinggi fixed
        if ir_hit and d_f is None:
            duty = config.MAX_DUTY
        else:
            duty = map_distance_to_duty(d_f if d_f is not None else 0, thr)

        out.vibrate_level(duty)
        out.beep(True)
    else:
        out.off()

    # Debug serial (boleh dimatiin untuk hemat)
    print("dist=", d_f, "thr=", round(thr,1), "score=", score, "IR=", ir_hit, "danger=", danger)

    time.sleep_ms(config.SAMPLE_MS)
