
PACKAGE=EQSysLogParser

##############################################################################
# do this while not in venv
venv:
	python -m venv .$(PACKAGE).venv

venv.clean:
	rm -rfd .$(PACKAGE).venv


##############################################################################
# do these while in venv
run: libs.quiet
	python $(PACKAGE).py


# libs make targets ###########################
libs: requirements.txt
	pip install -r requirements.txt

libs.quiet: requirements.txt
	pip install -q -r requirements.txt

libs.clean:
	pip uninstall -r requirements.txt


# exe make targets ###########################
exe: libs
	pyinstaller --onefile $(PACKAGE).py

exe.clean: libs.clean
	rm -rfd build
	#rm -rfd dist
	rm dist/$(PACKAGE).exe
	rm $(PACKAGE).spec



# general make targets ###########################

all: libs exe

all.clean: libs.clean exe.clean

clean: all.clean

