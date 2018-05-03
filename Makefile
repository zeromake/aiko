.PHONY: release build

release: build
	twine upload dist/*

build:
	rm -rf ./dist
	python setup.py sdist
	python setup.py bdist_wheel
	python setup.py bdist_egg
