all: build

COMPOSE=docker compose -f docker/docker-compose.yaml

build up watch:
	$(COMPOSE) $@ perimeter

eslint:
	$(COMPOSE) build eslint
	$(COMPOSE) run --rm eslint /fe/node_modules/.bin/eslint

pylint-image:
	$(COMPOSE) build pylint

pylint: pylint-image
	$(COMPOSE) run --rm pylint $@ --rcfile /app/pylint.cfg /app/

pycodestyle: pylint-image
	$(COMPOSE) run --rm pylint $@ /app/

createsuperuser:
	docker exec -it perimeter python manage.py $@
