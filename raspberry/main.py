import pprint
import time
from datetime import datetime
from threading import Event, Thread

from gpiozero import LED
from kubernetes import config, client

white_led = LED(2)
blue_led = LED(3)
green_led_1 = LED(4)
green_led_2 = LED(17)
yellow_led = LED(27)
red_led = LED(22)

NAMESPACE = "default"
HPA_NAME = "kubernetes-playground-api"
LABEL_SELECTOR = "app=kubernetes-playground-api"


config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")
k8s_core = client.CoreV1Api()
k8s_autoscaling = client.AutoscalingV1Api()


def get_pods_running(label_selector: str = LABEL_SELECTOR, namespace: str = NAMESPACE) -> int:
    result = k8s_core.list_namespaced_pod(namespace, label_selector=label_selector)
    return len(list(filter(lambda i: i.status.phase == "Running", result.items)))


def get_hpa_desired(name: str = HPA_NAME, namespace: str = NAMESPACE) -> (int, int):
    result = k8s_autoscaling.read_namespaced_horizontal_pod_autoscaler(name, namespace)
    return result.spec.max_replicas, result.status.desired_replicas


def _blink_led(led: LED, event: Event):
    while not event.is_set():
        led.on()
        time.sleep(0.5)
        led.off()


def blink_led(led: LED) -> (Thread, Event):
    event = Event()
    thread = Thread(target=_blink_led, args=(led, event))
    thread.start()
    return thread, event


def stop_blinking(thread: Thread, event: Event):
    event.set()
    thread.join()


def blink_leds():
    led_thresholds = [
        (blue_led, 0),
        (green_led_1, 10),
        (green_led_2, 25),
        (yellow_led, 60),
        (red_led, 85),
    ]
    thread, event = None, None
    while True:
        max_replicas, desired_replicas = get_hpa_desired()
        led_to_blink_on_decrease = None
        led_to_blink_on_increase = None
        pods_running = get_pods_running()
        running_pods_percentage = (pods_running / max_replicas) * 100
        for led, threshold in led_thresholds:
            if running_pods_percentage >= threshold:
                led.on()
                led_to_blink_on_decrease = led
            else:
                led.off()
                if not led_to_blink_on_increase:
                    led_to_blink_on_increase = led

        time.sleep(1)
        if pods_running > desired_replicas:
            if not thread and not event and led_to_blink_on_decrease:
                thread, event = blink_led(led_to_blink_on_decrease)

        elif pods_running < desired_replicas:
            if not thread and not event and led_to_blink_on_increase:
                thread, event = blink_led(led_to_blink_on_increase)

        else:
            if thread and event:
                stop_blinking(thread, event)
                thread = None
                event = None


def main():
    white_led.on()
    k8s_autoscaling.patch_namespaced_horizontal_pod_autoscaler(HPA_NAME, NAMESPACE,{"spec": {"minReplicas": 1, "maxReplicas": 2}})
    blink_leds()


if __name__ == '__main__':
    try:
        print("Running...")
        main()
    except KeyboardInterrupt:
        print("Exiting...")
