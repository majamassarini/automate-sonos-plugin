.PHONY: prepare-venv test coverage docs

VENV                 ?=
PYTHON                = $(if $(VENV),$(CURDIR)/$(VENV)/bin/python3,python3)
SPHINXBUILD           = $(if $(VENV),$(CURDIR)/$(VENV)/bin/sphinx-build,sphinx-build)
AUTOMATE_HOME_BRANCH ?=

prepare-venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install ".[dev,docs]"
	$(if $(AUTOMATE_HOME_BRANCH),$(VENV)/bin/pip install --force-reinstall "git+https://github.com/majamassarini/automate-home.git@$(AUTOMATE_HOME_BRANCH)")

test:
	$(PYTHON) -m coverage run -m unittest discover -s soco_plugin/tests -p 'test*.py' -v

coverage: test
	$(PYTHON) -m coverage report -m
	$(PYTHON) -m coverage html
	open htmlcov/index.html

docs:
	$(MAKE) -C docs html SPHINXBUILD=$(SPHINXBUILD)
