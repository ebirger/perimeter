all: build

COMPOSE=docker compose -f docker/docker-compose.yaml

build up watch:
	$(COMPOSE) $@ perimeter

pylint:
	$@ --rcfile be/pylint.cfg be/

pycodestyle:
	$@ be/

eslint:
	$(COMPOSE) build eslint
	$(COMPOSE) run --rm eslint /fe/node_modules/.bin/eslint

createsuperuser:
	docker exec -it perimeter python manage.py $@
