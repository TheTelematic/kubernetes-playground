push-code-to-raspberry:
	ssh arturo@raspberrypi.local -t "rm -r app/"
	scp -r raspberry/ arturo@raspberrypi.local:/home/arturo/app

run-raspberry: push-code-to-raspberry
	ssh arturo@raspberrypi.local -t "python3.13 app/main.py"
