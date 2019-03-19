.PHONY: build chain

test:
	POSTGRES_DB_NAME=testark CHAIN_CONFIG_FOLDER="tests/config/" py.test -vv -s -x $(ARGS)

remove-pyc:
	find . -name "*.pyc" -delete

create-migrations:
	cd chain/plugins/database; python create_migrations.py

migrate:
	python chain/plugins/database/migrate.py

black:
	black .

black-check:
	black --check .

profile:
	python -m cProfile -o spongebob.prof spongebob.py

snakeviz:
	snakeviz spongebob.prof

build:
	docker-compose build

chain:
	docker-compose up blockchain

p2p:
	docker-compose up chain-p2p
