all: build

build up watch:
	docker compose -f docker/docker-compose.yaml $@

pylint:
	$@ --rcfile be/pylint.cfg be/

pycodestyle:
	$@ be/

createsuperuser:
	docker exec -it perimeter python manage.py $@
