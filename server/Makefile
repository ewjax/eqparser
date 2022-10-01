
PACKAGE=EQSysLogParser

##############################################################################
# do this while not in venv
venv:
	python3.9 -m venv .eslp

venv.clean:
	rm -rfd .eslp



##############################################################################
# do these while in venv
run: libs.quiet
	python3.9 $(PACKAGE).py


# libs make targets ###########################
libs: requirements.txt
	pip3 install -r requirements.txt

libs.quiet: requirements.txt
	pip3 install -q -r requirements.txt

libs.clean:
	pip3 uninstall -r requirements.txt


# install make targets ###########################
#DIRS=dist/data dist/xxx
DIRS=dist/data
install: exe
	#cp $(PACKAGE).ini* ./dist
	$(shell mkdir $(DIRS))
	#cp ./data/*.dat ./dist/data/

install.clean: exe.clean
	#rm -rfd dist/$(PACKAGE).ini
	#rm -rfd dist/data


# general make targets ###########################

all: libs install

all.clean: libs.clean install.clean

clean: all.clean
