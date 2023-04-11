.PHONY: init
init:
	pip3 install -r requirements.txt

.PHONY: run
run:
	python3 main.py

.PHONY: docker
docker:
    docker build -t ghcr.io/tbxark/poe-telegram-bot:latest .
    docker push ghcr.io/tbxark/poe-telegram-bot:latest
