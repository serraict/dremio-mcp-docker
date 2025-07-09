.PHONY: build-images console

build-images:
	docker compose build --no-cache
console:
	docker compose up
