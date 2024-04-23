BUILD_FOLDER := _build
SNAPSHOTS_FOLDER := __SNAPSHOTS__
SMARTPY_CLI_PATH := $(BUILD_FOLDER)/smartpy-cli
PYTHONPATH := $(SMARTPY_CLI_PATH):$(shell pwd)

COMPILATIONS := $(filter-out %/__init__.py, $(wildcard compilations/*.py))
TESTS := $(filter-out %/__init__.py, $(wildcard tests/*.py))


touch_done=@mkdir -p $(@D) && touch $@;

all: install-dependencies

##
## + Compilations
##
compilations/%: compilations/%.py install-dependencies
	@$(SMARTPY_CLI_PATH)/SmartPy.sh compile $< $(SNAPSHOTS_FOLDER)/compilation/$*

compile-contracts: $(COMPILATIONS:%.py=%) setup_env
	@echo "Compiled contracts."

##
## - Compilations
##

##
## + Tests
##
tests/%: tests/%.py install-dependencies
	@$(SMARTPY_CLI_PATH)/SmartPy.sh test $< $(SNAPSHOTS_FOLDER)/test/$* --html

test-contracts: $(TESTS:%.py=%) setup_env
	@echo "Tested contracts."

##
## - Tests
##

##
## + Deployments
##
common_scripts = deployments/deployment.py deployments/utils.py

deploy-ghostnet: deployments/ghostnet/configuration.py $(common_scripts) compile-contracts
	python3 deployments/deployment.py ghostnet

deploy-mainnet: deployments/mainnet/configuration.py $(common_scripts) compile-contracts
	python3 deployments/deployment.py mainnet

##
## - Deployments
##

fmt-check:
	python3 -m black --check .

fmt-fix:
	python3 -m black .

export PYTHONPATH
setup_env: # Setup environment variables

clean:
	@rm -rf $(BUILD_FOLDER)

##
## + Install Dependencies
##
install-smartpy: $(BUILD_FOLDER)/install-smartpy
$(BUILD_FOLDER)/install-smartpy:
	@rm -rf $(SMARTPY_CLI_PATH)
	@bash -c "bash <(curl -s https://legacy.smartpy.io/cli/install.sh) --prefix $(SMARTPY_CLI_PATH) --yes"
	$(touch_done)

install-dependencies: install-smartpy
	@pip3 install -r requirements.txt --quiet
##
## - Install dependencies
##
