all: build

build up:
	docker compose -f docker/docker-compose.yaml $@

createsuperuser:
	docker exec -it perimeter python manage.py $@
