
PACKAGE=EQParser

##############################################################################
# do this while not in venv
venv:
	python -m venv .venv

venv.clean:
	rm -rfd .venv



##############################################################################
# do these while in venv
run: libs.quiet
	py $(PACKAGE).py


# libs make targets ###########################
libs: requirements.txt
	pip install -r requirements.txt

libs.quiet: requirements.txt
	pip install -q -r requirements.txt

libs.clean:
	pip uninstall -r requirements.txt


# exe make targets ###########################
exe: libs
	pyinstaller --onefile --icon data/icons/diamond.ico $(PACKAGE).py

exe.clean: libs.clean
	rm -rfd build
	#rm -rfd dist
	rm dist/$(PACKAGE).exe


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


# zip make targets ###########################
zip: install
	cd dist && zip -r $(PACKAGE).zip * -x $(PACKAGE).ini

zip.clean:
	rm dist/$(PACKAGE).zip


# general make targets ###########################

all: libs exe install zip

all.clean: libs.clean exe.clean install.clean zip.clean

clean: all.clean
