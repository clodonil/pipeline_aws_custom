.PHONY: help clean clean-build coverage lint mut
.DEFAULT: help

help:
	@echo "make clean"
	@echo "       prepare development environment, use only once"
	@echo "make clean-build"
	@echo "       Clear all build directories"
	@echo "make coverage"
	@echo "       run coverage command cli in development features"
	@echo "make lint"
	@echo "       run lint"
	@echo "make test"
	@echo "       run tests"

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . | grep -E "__pycache__|.pyc" | xargs rm -rf

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

coverage:
	pytest --cov-report xml --cov=.

test:
	pytest --verbose --color=yes
	coverage run --source=. -m pytest
	coverage report -m

lint:
	flake8 --ignore E305,E501 --exclude .git,__pycache__
	bandit -r -lll .
	
mut:	
	mut.py  --target templates/*  --unit-test tests/  --runner pytest --coverage
