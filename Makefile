.PHONY: build chain

test:
	POSTGRES_DB_NAME=testark CHAIN_CONFIG_FOLDER="tests/config/" py.test -vv -s -x $(ARGS)

remove-pyc:
	find . -name "*.pyc" -delete

create-migrations:
	cd chain/plugins/database; python create_migrations.py

black:
	black . --target-version=py37

black-check:
	black --check .

profile:
	python -m cProfile -o spongebob.prof spongebob.py

snakeviz:
	snakeviz spongebob.prof

build:
	docker-compose build

blockchain:
	docker-compose up -d blockchain

migrate:
	docker-compose run blockchain python chain/plugins/database/migrate.py

database:
	docker-compose up -d chain-db
	sleep 3s

start:
	make database
	make migrate
	docker-compose up -d

blockchain-logs:
	docker-compose logs --tail 50 -f blockchain

p2p-logs:
	docker-compose logs --tail 50 -f chain-p2p

huey-logs:
	docker-compose logs --tail 50 -f chain-huey
