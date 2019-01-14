test:
	py.test -v -s -x $(ARGS)

remove-pyc:
	find . -name "*.pyc" -delete
