build:
	docker compose build

run: build
	docker compose up

createsuperuser:
	docker exec -it perimeter python manage.py $@
