.ONESHELL:
SHELL := /bin/bash
SRC = $(wildcard nbs/*.ipynb)


sync:
	nbdev_update_lib

docs_serve: docs
	nbdev_build_docs
	cd docs && bundle exec jekyll serve

test:
	nbdev_test_nbs


nbdev-all:
	nbdev_clean_nbs
	nbdev_build_lib
	nbdev_test_nbs

release:
	nbdev_clean_nbs
	nbdev_build_lib
	nbdev_bump_version
	rm -rf dist
	python setup.py sdist bdist_wheel
	twine upload --repository pypi dist/*