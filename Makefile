.PHONY: init
init:
	pip3 install -r requirements.txt

.PHONY: run
run:
	python3 main.py

.PHONY: image
image:
	docker build -t ghcr.io/tbxark/poe-telegram-bot:latest . && \
	docker push ghcr.io/tbxark/poe-telegram-bot:latest

