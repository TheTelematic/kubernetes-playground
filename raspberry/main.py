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


def list_pods():
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_namespaced_pod("default")
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


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
            list_pods()
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
