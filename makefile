.PHONY: build-images

build-images:
	docker compose build --no-cache
console:
	docker compose up
