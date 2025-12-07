docker_hub_image_name = thetelematic95/kubernetes_playground
image_name ?= kubernetes_playground
image_tag ?= latest
target ?= app

export DOCKER_BUILDKIT = 1

install-requirements:
	python -m pip install -r requirements.txt

build:
	docker build -t ${image_name}:${image_tag} --target kubernetes_playground_${target} . --build-arg BUILD_TIMESTAMP=$(shell date -u +'%Y-%m-%dT%H:%M:%SZ')

deploy-local:
	helm upgrade --install --wait kubernetes-playground kubernetes/chart

undeploy:
	-helm uninstall kubernetes-playground

check-chart:
	helm template --debug kubenetes-playground kubernetes/chart
	helm lint kubernetes/chart

publish:
	docker tag ${image_name}:${image_tag} ${docker_hub_image_name}:latest
	docker push ${docker_hub_image_name}:latest
