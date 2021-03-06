.PHONY: all lint test test-cov install dev

lint:
	q2lint
	flake8

test: all
	py.test

test-cov: all
	py.test --cov=q2_american_gut

install: all
	python setup.py install

dev: all
	pip install -e .
