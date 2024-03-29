build:
	docker compose build
start:
	docker compose up -d

shell:
	docker compose run --rm bot bash

clean:
	docker compose down

logs:
	docker compose logs -f bot

restart:
	docker compose restart bot