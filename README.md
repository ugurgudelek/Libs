# LIBS
[![](https://github.com/ugurgudelek/Libs/raw/master/input/logo.png)](http://www.biyans.com/)

## Soil analysis tool

1. Read data from Oceanview Spectrometers.
2. Find nearby element peaks.
3. Use pre-built calibration curves to calculate necessary amount of elements.
4. [*not-implemented*] Add these numbers to TBS system.


### Installation

1. Download this repo.
2. Below lines will create **libs** conda environment.  

|this|or that|
|---|---|
|`conda env create -f environment.yml`|`install.bat`|


3.  While spectrometers plugged in, install **prerequisites/libusb-win32-bin-1.2.6.0**. This will add spectrometers to device manager.



### Run
Above script should be run in **./src** folder.

|this|or that|
|---|---|
|<code>activate libs</code><br><code>python gui.py</code>|`run.bat`|
