import time

try:
    import RPi.GPIO as GPIO
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"RPi.GPIO import edilemedi: {exc}")

# Varsayilan pinler (BCM)
PINS = {
    "ena": 12,
    "enb": 13,
    "in1": 23,
    "in2": 24,
    "in3": 27,
    "in4": 22,
}
# ENA/ENB jumper ile 5V'a bagliysa PWM'e gerek yok; sabit hiz için True yap.
USE_JUMPER_NO_PWM = True


def main() -> None:
    print("L298N manuel test (PWM'siz jumper modu destekli) basliyor.")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    ena = enb = None
    if USE_JUMPER_NO_PWM:
        GPIO.output(PINS["ena"], GPIO.HIGH)
        GPIO.output(PINS["enb"], GPIO.HIGH)
    else:
        ena = GPIO.PWM(PINS["ena"], 1000)
        enb = GPIO.PWM(PINS["enb"], 1000)
        ena.start(0)
        enb.start(0)

    try:
        # Ileri
        print("Ileri...")
        GPIO.output(PINS["in1"], GPIO.HIGH)
        GPIO.output(PINS["in2"], GPIO.LOW)
        GPIO.output(PINS["in3"], GPIO.LOW)
        GPIO.output(PINS["in4"], GPIO.HIGH)
        if not USE_JUMPER_NO_PWM:
            ena.ChangeDutyCycle(60)
            enb.ChangeDutyCycle(60)
        time.sleep(2)

        # Geri
        print("Geri...")
        GPIO.output(PINS["in1"], GPIO.LOW)
        GPIO.output(PINS["in2"], GPIO.HIGH)
        GPIO.output(PINS["in3"], GPIO.HIGH)
        GPIO.output(PINS["in4"], GPIO.LOW)
        time.sleep(2)

        print("Duruyor...")
        if USE_JUMPER_NO_PWM:
            GPIO.output(PINS["in1"], GPIO.LOW)
            GPIO.output(PINS["in2"], GPIO.LOW)
            GPIO.output(PINS["in3"], GPIO.LOW)
            GPIO.output(PINS["in4"], GPIO.LOW)
        else:
            ena.ChangeDutyCycle(0)
            enb.ChangeDutyCycle(0)
    finally:
        if ena:
            ena.stop()
        if enb:
            enb.stop()
        GPIO.cleanup()
        print("GPIO temizlendi, test bitti.")


if __name__ == "__main__":
    main()
