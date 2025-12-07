import pprint
import time
from datetime import datetime

from gpiozero import LED
from kubernetes import config, client

white_led = LED(2)
blue_led = LED(3)
green_led_1 = LED(4)
green_led_2 = LED(17)
yellow_led = LED(27)
red_led = LED(22)


HPA_NAME = "kubernetes-playground-api"
LABEL_SELECTOR = "app=kubernetes-playground-api"

config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")
k8s_core = client.CoreV1Api()
k8s_autoscaling = client.AutoscalingV1Api()


def get_pods_running(label_selector: str = LABEL_SELECTOR, namespace: str = "default") -> int:
    result = k8s_core.list_namespaced_pod(namespace, label_selector=label_selector)
    return len(list(filter(lambda i: i.status.phase == "Running", result.items)))


def get_hpa(name: str = HPA_NAME, namespace: str = "default") -> (int, int):
    result = k8s_autoscaling.read_namespaced_horizontal_pod_autoscaler(name, namespace)
    return result.spec.min_replicas, result.spec.max_replicas


def scale_down(name: str = HPA_NAME, namespace: str = "default"):
    print("Scaling down...")
    k8s_autoscaling.patch_namespaced_horizontal_pod_autoscaler(name, namespace, {"spec": {"min_replicas": 3, "max_replicas": 5}})
    print("Scaling down completed")


def scale_up():
    print("Scaling up...")
    print("Scaling up completed")


def blink_leds():
    led_buckets = {
        0: blue_led,
        10: green_led_1,
        25: green_led_2,
        50: yellow_led,
        80: red_led,
    }
    candidate_to_scale_down_at = None
    candidate_to_scale_up_at = None
    while True:
        min_replicas, max_replicas = get_hpa()
        pods_running = get_pods_running()
        percentage = (pods_running / max_replicas) * 100
        for bucket, led in led_buckets.items():
            if percentage >= bucket:
                led.on()
            else:
                led.off()

        time.sleep(1)
        if percentage < 10 and not candidate_to_scale_down_at:
            candidate_to_scale_down_at = datetime.now()
        elif percentage > 90 and not candidate_to_scale_up_at:
            candidate_to_scale_up_at = datetime.now()

        elif (datetime.now() - candidate_to_scale_down_at).total_seconds() > 60:
            scale_down()
        elif (datetime.now() - candidate_to_scale_up_at).total_seconds() > 60:
            scale_up()


def main():
    white_led.on()
    blink_leds()


if __name__ == '__main__':
    try:
        print("Running...")
        main()
    except KeyboardInterrupt:
        print("Exiting...")
