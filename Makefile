push-code-to-raspberry:
	@ssh arturo@raspberrypi.local -t "rm -r app/" > /dev/null
	@scp -r raspberry/ arturo@raspberrypi.local:/home/arturo/app > /dev/null

run-raspberry: push-code-to-raspberry
	@ssh arturo@raspberrypi.local -t "sudo apt-get install -y python3-kubernetes > /dev/null; sudo python3.13 app/main.py"
