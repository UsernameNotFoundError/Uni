SYSTEM_PYTHON = python3
PYTHON        = .venv/bin/python

init:
	sudo apt-get -y install libmysqlclient-dev
	sudo apt-get install -y python3-dev
	sudo apt-get -y install python3-testresources

install:
	rm -rf .venv 2> /dev/null || true
	$(SYSTEM_PYTHON) -m venv .venv
	chmod +x .venv/bin/activate
	.venv/bin/activate 
	$(PYTHON) -m pip install -r ./src/requirements.txt

wsl_info:
	awk '/nameserver/ { print $2 }' /etc/resolv.conf