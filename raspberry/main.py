import time

from gpiozero import LED
from kubernetes import config, client

white_led = LED(2)
blue_led = LED(3)
green_led_1 = LED(4)
green_led_2 = LED(17)
yellow_led = LED(27)
red_led = LED(22)


config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")
v1 = client.CoreV1Api()


def get_pods(label_selector: str, namespace: str = "default") -> int:
    ret = v1.list_namespaced_pod(namespace, label_selector=label_selector)
    return len(ret.items)


def blink_leds():
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
            n_pods = get_pods("app=kubernetes-playground-api")
            print(f"{n_pods} pods running")
            time.sleep(1)
            previous_led = led


def main():
    white_led.on()
    blink_leds()


if __name__ == '__main__':
    try:
        print("Running...")
        main()
    except KeyboardInterrupt:
        print("Exiting...")
