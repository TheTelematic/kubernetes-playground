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


def get_hpa(name: str = HPA_NAME, namespace: str = NAMESPACE) -> (int, int, float | None):
    result = k8s_autoscaling.read_namespaced_horizontal_pod_autoscaler(name, namespace)
    return result.spec.min_replicas, result.spec.max_replicas, result.status.current_cpu_utilization_percentage


def decrease_max_pods(name: str = HPA_NAME, namespace: str = NAMESPACE):
    print("Decreasing max pods...")
    min_replicas, max_replicas, _ = get_hpa()
    new_max_replicas = max(1, min_replicas, max_replicas - 1)
    k8s_autoscaling.patch_namespaced_horizontal_pod_autoscaler(name, namespace, {"spec": {"maxReplicas": new_max_replicas}})


def increase_max_pods(name: str = HPA_NAME, namespace: str = NAMESPACE):
    print("Increasing max pods...")
    min_replicas, max_replicas, _ = get_hpa()
    new_max_replicas = max(1, min_replicas, max_replicas + 1)
    k8s_autoscaling.patch_namespaced_horizontal_pod_autoscaler(name, namespace, {"spec": {"maxReplicas": new_max_replicas}})


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
    timestamp_to_decrease_at = None
    timestamp_to_increase_at = None
    thread, event = None, None
    while True:
        _, max_replicas, current_cpu_utilization_percentage = get_hpa()
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
        if current_cpu_utilization_percentage and current_cpu_utilization_percentage < 10 and not timestamp_to_decrease_at:
            print("Starting to decrease max pods...")
            timestamp_to_decrease_at = datetime.now()
            if led_to_blink_on_decrease:
                thread, event = blink_led(led_to_blink_on_decrease)

        elif current_cpu_utilization_percentage and current_cpu_utilization_percentage > 90 and not timestamp_to_increase_at:
            print("Starting to increase max pods...")
            timestamp_to_increase_at = datetime.now()
            if led_to_blink_on_increase:
                thread, event = blink_led(led_to_blink_on_increase)

        elif timestamp_to_decrease_at and (datetime.now() - timestamp_to_decrease_at).total_seconds() > 5:
            if thread and event:
                stop_blinking(thread, event)
                thread = None
                event = None
            decrease_max_pods()
            timestamp_to_decrease_at = None

        elif timestamp_to_increase_at and (datetime.now() - timestamp_to_increase_at).total_seconds() > 5:
            if thread and event:
                stop_blinking(thread, event)
                thread = None
                event = None
            increase_max_pods()
            timestamp_to_increase_at = None


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
