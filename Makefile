.PHONY: up down install-mdns uninstall-mdns

AVAHI_SERVICE_SRC = docker/avahi-mqtt.service
AVAHI_SERVICE_DST = /etc/avahi/services/mqtt.service

up:
	docker compose up -d

down:
	docker compose down

install-mdns:
	sudo cp $(AVAHI_SERVICE_SRC) $(AVAHI_SERVICE_DST)
	sudo systemctl reload avahi-daemon

uninstall-mdns:
	sudo rm -f $(AVAHI_SERVICE_DST)
	sudo systemctl reload avahi-daemon

