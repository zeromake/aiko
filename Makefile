.PHONY: release build tox test cov

release: build
	twine upload dist/*

build:
	rm -rf ./dist
	python setup.py sdist
	python setup.py bdist_wheel
	python setup.py bdist_egg

tox:
	tox

test: tox
	pytest -s -v --cov-report term --cov=aiko tests

cov:
	pytest -s -v --cov-report term --cov-report html --cov aiko tests
