.PHONY: build chain docs

test:
	POSTGRES_DB_NAME=testark CHAIN_CONFIG_FOLDER="tests/config/" py.test -vv -s -x $(ARGS)

cov-html:
	POSTGRES_DB_NAME=testark CHAIN_CONFIG_FOLDER="tests/config/" py.test --cov=./chain --cov-report html

remove-pyc:
	find . -name "*.pyc" -delete

create-migrations:
	CHAIN_CONFIG_FOLDER=ark/devnet python -m chain.plugins.database.create_migrations

lint:
	flake8 .

black:
	black .

black-check:
	black --check .

profile:
	CHAIN_CONFIG_FOLDER=ark/devnet python -m cProfile -o spongebob.prof spongebob.py

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
	@docker-compose exec chain-db bash -c "echo -n 'Waiting for chain-db to be ready: '; while true ; do if ! psql -l -U $${POSTGRES_DB_USER:-postgres} >/dev/null 2>&1 ; then echo -n '.' ; sleep 0.2 ; else echo ' Done.' ; break ; fi ; done"

start:
	make database
	make migrate
	docker-compose up -d

restart:
	docker-compose stop
	docker-compose up -d

blockchain-logs:
	docker-compose logs --tail 50 -f blockchain

p2p-logs:
	docker-compose logs --tail 50 -f chain-p2p

huey-logs:
	docker-compose logs --tail 50 -f chain-huey

docs:
	cd docs && rm -r _build && CHAIN_CONFIG_FOLDER=../ark/devnet make html
	@echo "\033[95m\n\nBuild successful! View the docs homepage at docs/_build/html/index.html.\n\033[0m"
