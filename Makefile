.PHONY: chain

test:
	py.test -vv -s -x $(ARGS)

remove-pyc:
	find . -name "*.pyc" -delete


create-migrations:
	cd chain/plugins/database; python create_migrations.py

migrate:
	cd chain/plugins/database; python migrate.py

black:
	black .

black-check:
	black --check .


profile:
	python -m cProfile -o spongebob.prof spongebob.py

snakeviz:
	snakeviz spongebob.prof

chain:
	docker-compose up blockchain

p2p:
	docker-compose up chain-p2p