import time

from gpiozero import LED

white_led = LED(2)
blue_led = LED(3)
green_led_1 = LED(4)
green_led_2 = LED(17)
yellow_led = LED(27)
red_led = LED(22)


def main():
    white_led.on()
    leds = [
        blue_led,
        green_led_1,
        green_led_2,
        yellow_led,
        red_led,
    ]
    previous_led = leds[0]
    while True:
        for led in leds:
            previous_led.off()
            led.on()
            time.sleep(1)
            previous_led = led

if __name__ == '__main__':
    main()
