all: build

build up watch:
	docker compose -f docker/docker-compose.yaml $@

createsuperuser:
	docker exec -it perimeter python manage.py $@
