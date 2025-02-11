DC = docker-compose

.PHONY: all build up down logs migrations migrate test fclean re

# Default-Ziel: bei "make" wird alles gestartet und migrations und migrate ist im dockefile!
all: build up

build:
	$(DC) build

up:
	$(DC) up -d

down:
	$(DC) down

logs:
	$(DC) logs -f

migrations:
	$(DC) exec backend python manage.py makemigrations

migrate:
	$(DC) exec backend python manage.py migrate

test:
	$(DC) exec backend sh -c "python manage.py flush --no-input && python helper_scripts/test_auth.py"

testuser:
	$(DC) exec backend sh -c "python manage.py shell < helper_scripts/create_testuser.py"

test15:
	$(DC) exec backend sh -c "python manage.py shell < helper_scripts/create_fifteen_testusers.py"

# Wirklich alles löschen: Container, Images, Volumes, Netzwerke
fclean:
	$(DC) down --rmi all --volumes --remove-orphans
	docker system prune -af

# Neu aufsetzen: Erst alles löschen, dann neu starten
re: fclean all
