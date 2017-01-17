all : defns Timekeeper lxc_command

defns:
	python definitions.py

Timekeeper:
	cd dilation-code; sudo make build; sudo make install 

lxc_command:	
	cd lxc-command; make

large_linear_disabled:
	cd tests/large_linear; sudo python large_linear.py; cd ../../; sudo python deploy.py $(shell pwd)/tests/large_linear -D

large_linear_enabled:
	cd tests/large_linear; sudo python large_linear.py; cd ../../; sudo python deploy.py $(shell pwd)/tests/large_linear

large_ring_disabled:
	cd tests/large_ring; sudo python large_ring.py; cd ../../; sudo python deploy.py $(shell pwd)/tests/large_ring -D

large_ring_enabled:
	cd tests/large_ring; sudo python large_ring.py; cd ../../; sudo python deploy.py $(shell pwd)/tests/large_ring
