PYTHON = python2

build:
		$(PYTHON) setup.py build

install:
		$(PYTHON) setup.py install

test: pep8
		$(PYTHON) setup.py test

coverage:
		coverage run --source=src setup.py test

clean:
		$(PYTHON) setup.py clean

console:
		cd src && $(PYTHON)

upload:
		$(PYTHON) setup.py sdist upload

pep8:
		pep8 --max-line-length 120 src tests

.PHONY: build install test coverage clean console upload pep8
