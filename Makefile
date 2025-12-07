push-code-to-raspberry:
	@ssh arturo@raspberrypi.local -t "rm -r app/" > /dev/null
	@scp -r raspberry/ arturo@raspberrypi.local:/home/arturo/app > /dev/null

run-raspberry: push-code-to-raspberry
	@ssh arturo@raspberrypi.local -t "sudo apt-get install -y python3-kubernetes > /dev/null; sudo python3.13 app/main.py"

set-replicas:
	@minReplicas=$1
	@maxReplicas=$2

	@kubectl patch hpa/kubernetes-playground-api -p '{"spec": {"minReplicas": ${minReplicas}, "maxReplicas": ${maxReplicas}}}'
