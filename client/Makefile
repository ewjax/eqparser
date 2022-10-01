
PACKAGE=SnekParser

run:
	py $(PACKAGE).py


# exe make targets ###########################
exe:
	pyinstaller --onefile $(PACKAGE).py

exe.clean:
	rm *.spec
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

all: exe install zip

all.clean: exe.clean install.clean zip.clean

clean: all.clean
