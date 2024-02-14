all: help

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  install                     to install the project"
	@echo "  lint                        to lint backend code (flake8)"
	@echo "  test                        to run test suite"


install:
	pip3 install -e .[dev]

lint:
	flake8 pyiso4 tests --max-line-length=120 --ignore=N802

test:
	python -m unittest discover -s tests