APP_NAME=bot-ferme
CHART_PATH=src/backend/deploy/charts/bot-ferme
IMAGE_NAME=bot-ferme-backend
TAG=latest

.PHONY: help build install test status logs top up stop uninstall ping dev down

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

ping:
	@echo "Pong!"
generate-keys:
	mkdir -p src/backend/certs
	openssl genrsa -out src/backend/certs/private.pem 2048
	openssl rsa -in src/backend/certs/private.pem -outform PEM -pubout -out src/backend/certs/public.pem

build:
	eval $$(minikube docker-env) && docker build -t $(IMAGE_NAME):$(TAG) ./src/backend

install: build
	helm upgrade --install $(APP_NAME) $(CHART_PATH)

status:
	@kubectl get pods,svc,hpa -l app=$(APP_NAME)

logs:
	@kubectl logs -f -l app=$(APP_NAME) -c backend

top:
	@kubectl top pods -l app=$(APP_NAME)

stop:
	@echo "Stopping processes on port 8000..."
	@fuser -k 8000/tcp || true

up: stop
	docker-compose up --build -d

down:
	docker-compose down

dev: stop
	@echo "\033[32m[INFO]\033[0m Swagger (K8s): \033[34mhttp://127.0.0.1:8000/docs\033[0m"
	@kubectl port-forward svc/bot-ferme-backend-svc 8000:8000

test:
	@helm test $(APP_NAME) --logs

uninstall:
	helm uninstall $(APP_NAME)