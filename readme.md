# Usage Instructions

## Windows 
Create a virtual environment and install the dependencies:

    python -m pip install -r dependencies.txt
	
Install the ECB extension seperately from source:

	cd pyECB
	python setup.py install
	
## Linux
- Make sure to adjust `pyECB/setup.py` accordingly to compile for Linux.
- Install [Pylon](https://www.baslerweb.com/en/sales-support/downloads/software-downloads/pylon-supplementary-package-for-mpeg4-1-0-1-debian-linux-x86-64-bit/)
- Install the PyPylon [wheel](https://github.com/basler/pypylon/releases/download/1.6.0/pypylon-1.6.0-cp38-cp38-linux_x86_64.whl) (Python 3.8)
