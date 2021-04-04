all: help

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  lint                        to lint backend code (flake8)"
	@echo "  test                        to run test suite"

lint:
	flake8 pyiso4 --max-line-length=120 --ignore=N802

test:
	python -m unittest discover -s tests