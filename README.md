# STVID

## Introduction
STVID (satellite tools for video) is a set of applications for observing the night sky with video cameras and detecting, measuring and identifying satellites in these observations. 
 
![Example setup and results](img/example_setup.jpg  "Example setup and results")

STVID provides the following features:

-  Automatic start and end of data acquisition
- Compression of raw video frames using the maximum temporal pixel method ([Gural & Segon 2009](https://ui.adsabs.harvard.edu/abs/2009JIMO...37...28G/abstract))
- Detection of satellites in position and time using the 3D Hough transform ([Dalitz et al. 2017](https://www.ipol.im/pub/art/2017/208/))
- Fast calculation of satellite predictions using different orbital catalogs of two-line elements (TLEs)
- Matching and identification of detected satellites against predictions
- Output results in [IOD format](http://www.satobs.org/position/IODformat.html) for publishing on [SeeSat-L](http://www.satobs.org/seesat/index.html)

## Table of Contents

1. [Requirements](#requirements)
1. [Installation](#installation)
1. [Configuration](#configuration)
1. [Operation](#operation)
1. [Supported hardware](#supported-hardware)

## Requirements

- A computer desktop or single board computer like a Raspberry PI) with a linux operating system for running STVID
- An internet connection to allow time synchronization using the Network Time Protocol (NTP)
- An analog video or digital CMOS camera. Currently supported cameras are:
	- Any camera working with OpenCV
	- ZWO ASI cameras
	- Raspberry Pi HQ camera
- A fast photographic lens, F/1.8 or faster, capable of delivering a pixel scale of 30 to 60 arsec/pix
- (optional) A weather proof CCTV housing

## Installation

To install STVID, several dependencies need to be met. The following sections will detail the installation. The system wide installation commands provided here are specific for the Ubuntu 22.04 operating system, but similar software packages will be available for other operating systems.

<details>

### Dependencies

The following assumes the dependencies are installed in `$HOME/software`. Adjust this as necessary. To create this directory, run the following command.
```bash
mkdir -p $HOME/software                                  # Create directory
```

#### hough3dlines

The [hough3dlines](https://gitlab.com/pierros/hough3d-code) application is used to detect satellite trails in 3 dimensions (x and y position over time). The following commands will download, compile and install the `hough3dlines` executable in `/usr/local/bin`.
```bash
sudo apt install git make g++ libeigen3-dev              # Install dependencies
cd $HOME/software                                        # Goto directory
git clone https://gitlab.com/pierros/hough3d-code.git    # Clone repository
cd $HOME/software/hough3d-code                           # Goto directory
make                                                     # Compile application
sudo cp hough3dlines /usr/local/bin/                     # Install executable
make test                                                # Test installation (optional)
```

#### satpredict

Predictions of satellite positions, using two-line elements (TLEs), are computed using [satpredict](https://github.com/cbassa/satpredict).

```bash
sudo apt install make                                     # Install dependencies
cd $HOME/software                                        # Goto directory
git clone https://github.com/cbassa/satpredict.git       # Clone repository
cd $HOME/software/satpredict                             # Goto directory
make                                                     # Compile application
sudo make install                                        # Install executable
```

#### source-extractor

Stars are detected, and their positions and instrumental fluxes measured, using the `source-extractor` application. Depending on the operating system, this application can be known as the `source-extractor`, `sextractor` or `sex` executables. STVID expects this to be present in the path as `sextractor`, so the executable may need to be copied to the `sextractor` name. On Ubuntu 22.04 it is known as `source-extractor`.

```bash
sudo apt install source-extractor                              # Install binary
sudo cp /usr/bin/source-extractor /usr/local/bin/sextractor    # Copy executable
```

#### astrometry.net

The initial astrometric calibration of the STVID observations is performed with [astrometry.net](http://astrometry.net/). This application can be installed with the following command.

```bash
sudo apt install astrometry.net                                # Install binary
```
This application needs index files, which can be downloaded from [data.astrometry.net](http://data.astrometry.net/). For the widefield observations obtained with STVID, we need to download the 4100 series images (340MB in total). Check where the `add_path` variable in `/etc/astrometry.cfg` where the application will search for index files. Usually this is `/usr/share/astrometry`. These can be downloaded (as root) as follows.
```bash
sudo bash                                                      # Create a session with root privileges
cd /usr/share/astrometry                                       # Goto the add_path directory
wget -c http://data.astrometry.net/4100/index-4107.fits        # Download index files
wget -c http://data.astrometry.net/4100/index-4108.fits
wget -c http://data.astrometry.net/4100/index-4109.fits
wget -c http://data.astrometry.net/4100/index-4110.fits
wget -c http://data.astrometry.net/4100/index-4111.fits
wget -c http://data.astrometry.net/4100/index-4112.fits
wget -c http://data.astrometry.net/4100/index-4113.fits
wget -c http://data.astrometry.net/4100/index-4114.fits
wget -c http://data.astrometry.net/4100/index-4115.fits
wget -c http://data.astrometry.net/4100/index-4116.fits
wget -c http://data.astrometry.net/4100/index-4117.fits
wget -c http://data.astrometry.net/4100/index-4118.fits
wget -c http://data.astrometry.net/4100/index-4119.fits
exit                                                           # Exit session
```

#### ZWO ASI SDK and ASIStudio (optional)

For users that will operate ZWO ASI cameras, you will need to download and install the ZWO ASI SDK (software developers kit). Go to the ZWO ASI [software and drivers](https://astronomy-imaging-camera.com/software-drivers) page and click the *Developers* tab. Download the *Linux & Mac* SDK. This likely is called something like `ASI_linux_max_SDK_V1.28.tar.bz2`. This file can be extracted as follows (assuming the file is downloaded into the `$HOME` directory; adjust as necessary.

```bash
cd $HOME/software                                              # Goto directory
bzip2 -cd $HOME/ASI_linux_mac_SDK_V1.28.tar.bz2 | tar xvf -    # Extract archive
```

To operate and focus a ZWO ASI camera, it is recommended to install the ASIStudio software from ZWO ASI. This software will allow you to test the camera indepently from STVID and will help with pointing and focusing by giving you full interactive control of all camera properties. The installation of this software will also ensure that the ZWO ASI camera will get the necessary user permissions for it to operate with STVID.

To download ASIStudio, click the *Linux* tab at ZWO ASI [software and drivers](https://astronomy-imaging-camera.com/software-drivers) page and download the `x64` version of ASIStudio. This will likely download a file called `ASIStudio_V1.8.run`. The following commands will run the installer (assuming the file is downloaded in the `$HOME` directory).

```bash
chmod +x $HOME/ASIStudio_V1.8.run                              # Set permissions to execute installer
$HOME/ASIStudio_V1.8.run                                       # Execute installer
```
The ASIStudio installer will ask where to install the applications and to accept their license. Once installed, run the `ASICap` application with your ZWO ASI camera attached. The application will ask to you to provide the `sudo` credentials to install the `udev` rules setting the necessary user permissions. Once those are set, you should be able to operate your camera from within `ASICap`.

### Raspberry Pi Camera
If using a Raspberry Pi camera [picamerax](https://github.com/labthings/picamerax) is used. It can be installed by running:
`sudo pip install "picamerax[array]"`


### STVID installation

With the dependencies installed, we can install STVID using the following commands.

```bash
sudo apt install python-is-python3 python3-pip                 # Install python3 and pip
cd $HOME/software                                              # Goto directory
git clone https:/github.com/cbassa/stvid.git                   # Clone STVID repository
cd $HOME/software/stvid                                        # Goto directory
pip install -r requirements.txt                                # Install python requirements
```

</details>	
	
## Configuration

<details>

STVID is configured through a configuration file. A boiler plate configuration file is included as `configuration.ini-dist`. Copy this file to `configuration.ini` using the following command

```bash
cp configuration.ini-dist configuration.ini          # Copy configuration file
```

Most parameters in `configuration.ini` do not need to be changed, except for the following:

#### Observer
- `cospar`: A COSPAR number if you have one, use a number between 9900 and 9999 otherwise.
- `name`, `latitude`, `longitude`, `height`: Your name and location (latitude, longitude, height) in the WGS84 coordinate frame.

#### Setup
- `camera_type`: Your camera selection (`ASI` for ZWO ASI cameras, `CV2` for opencv cameras, `PI` for the Raspberry Pi HQ camera).
- `observations_path`: Directory where you want to store the observations.

#### Credentials
It is highly recommended to use the catalog of two-line elements (TLEs) from [space-track.org](https://www.space-track.org). Use the credentials of your account to download TLEs.

#### Elements
This section describes the TLE catalog that STVID downloads and how they are used and plotted.

- `tlepath`: Directory where you want to store the TLE catalogs

#### ZWO ASI cameras
For ZWO ASI cameras you need to specify the location of the ZWO ASI SDK libraries. For `x64` operating systems this is the `lib/x64/libASICamera2.so` shared library in the directory tree where you installed the SDK.

</details>	
	
## Operation

<details>

There are three applications in STVID that work together:

- `update_tle.py` to download orbital catalogs of two-line elements (TLEs).
- `acquire.py` to capture data from your camera and store them as FITS files.
- `process.py` to analyse the FITS files and determine satellite positions.

#### Updating TLEs

Assuming you have installed STVID in `$HOME/software/stvid` and your configuration is stored in `configuration.ini`, the TLE catalogs can be updated with the following command.
```bash
$HOME/software/stvid/update_tle.py -c $HOME/software/stvid/configuration.ini
```
This will download TLE catalogs from the following sources:

1. The master catalog called `catalog.tle` from [https://www.space-track.org](https://www.space-track.org). This requires your space-track.org credentials to be provided in `configuration.ini`.
1. The classified catalog `classfd.tle` from [Mike McCants](https://www.prismnet.com/~mmccants/tles/index.html). This catalog has TLEs for classified objects not present in `catalog.tle`.
1. The integrated elements `inttles.tle` from [Mike McCants](https://www.prismnet.com/~mmccants/tles/index.html). These are numerically integrated orbits converted into TLEs for objects at high altitudes.
1. Supplemental TLEs for Starlink satellites in `starlink.tle` from [celestrak.com](https://celestrak.org/NORAD/elements/supplemental/). These are TLEs computed from orbital ephemerides shared by the satellite operators and include predicted manouvers. These TLEs tend to be more accurate than those in `catalog.tle` which are based on observations.
1. Supplemental TLEs for OneWeb satellites in `oneweb.tle` from [celestrak.com](https://celestrak.org/NORAD/elements/supplemental/). These are TLEs computed from orbital ephemerides shared by the satellite operators and include predicted manouvers. These TLEs tend to be more accurate than those in `catalog.tle` which are based on observations.
	
</details>
	
## Supported hardware
TBD

## Installation on a Raspberry Pi for Acquistion.

**stvid** can be run on a Raspberry Pi 4B 8Gb with the Raspberry HQ Camera. Installation is not as easy as a on regular Linux and this installation step only supports the filming using acquire.py. The processing can be done on a dektop PC or laptop which has the complete installations of **sattools** and **stvid**. This guide is not complete nor correct. If you try this, please let me know what needs to be improved! 

### Requirements

Make sure the camera is enabled and tested using raspistill. For more info see: 

[https://www.raspberrypi.com/documentation/accessories/camera.html#raspistill](https://www.raspberrypi.com/documentation/accessories/camera.html#raspistill)


Using the HQ camera under python is currently (December 2021) only supported on Buster and not on the newer Bullseye. Run:

`cat /etc/os-release`

Check that it says `buster`. If you are reading this in the future, you should check if your version of the OS supports the camera under python.

For installing we need the OS to be up to date:

```
sudo apt-get update --allow-releaseinfo-change
sudo apt-get upgrade
```

Also cmake and some build tools need to be installed:

```
sudo apt-get install cmake
sudo apt install build-essential
```

**stvid** runs in pyhton3, it is probably already installed, but if not:

`sudo apt install python3`

Next the installation of OpenCv is needed. This is based on [https://www.pyimagesearch.com/2018/09/19/pip-install-opencv/](https://www.pyimagesearch.com/2018/09/19/pip-install-opencv/)

Consider using a VirtualEnv to run stvid on a separate python virtual environment.

```
cd
sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103
sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
sudo pip install opencv-contrib-python==4.1.0.25
```

This is a good moment to test OpenCV:

```
pi@allsky:~/stvid $ python3
Python 3.7.3 (default, Jan 22 2021, 20:04:44) 
[GCC 8.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import cv2
>>> cv2.__version__
'4.1.0'
>>> quit()
pi@allsky:~/stvid $ 
```

Install support for the Rapberry Pi cam in python:

`sudo pip install "picamerax[array]"`


The requirements are handled using pip. You can install requirements by running :

```
pip install -r requirements-pi.txt

```

### STVID

Stvid can be installed from this repository:

```
cd
git clone https://github.com/EelkeVisser/stvid.git
cd stvid
cp configuration.ini-dist configuration.ini
```

## Installation on a Raspberry Pi for Processing.

The processing can also be done on the Raspberry Pi, using process.py. But it has some dependecies that have no packages for the Raspberry, and need to be installed from source. This makes it difficult to install. I have it working and tried to document it here. But this guide is not complete nor correct. If you try this, please let me know what needs to be improved! The process.py make use of pgplot, and pgplot is dependent on libpng, bit does not work with the current version it needs an older version of libpng. Another problem is that giza is installed as replacement of pgplot, but does not seem usable from a quick test.

First we need to uninstall giza. Find if you have pgplotclib installed:

`sudo find / -name libcpgplot.so`

If so then it is probably giza, that needs to be uninstalled:

`sudo apt-get purge giza-dev`

Check if it has been removed.

`sudo find / -name libcpgplot.so`

Next we need an older version of libpng. I used version 1.4. Download it from [https://sourceforge.net/projects/libpng/files/libpng14/1.4.22/libpng-1.4.22.tar.gz/download](https://sourceforge.net/projects/libpng/files/libpng14/1.4.22/libpng-1.4.22.tar.gz/download)

And compile and install libpng:

```
cd libpng-1.4.22/
sudo ./install-sh 
sudo ./configure
sudo make
sudo make install
```

### PGPLOT

Next is pgplot based on [https://sites.astro.caltech.edu/~tjp/pgplot/install-unix.html](https://sites.astro.caltech.edu/~tjp/pgplot/install-unix.html)

It needs a fortran compiler:

```
sudo apt-get install gfortran
```

Download the source from [ftp://ftp.astro.caltech.edu/pub/pgplot/pgplot5.2.tar.gz](ftp://ftp.astro.caltech.edu/pub/pgplot/pgplot5.2.tar.gz) as follows:

```
cd /usr/local
mkdir src
cd src
wget ftp://ftp.astro.caltech.edu/pub/pgplot/pgplot5.2.tar.gz
gunzip -c pgplot5.2.tar.gz | tar xvof -
```

Make the target directory, go there to generate the makefile:

```
mkdir /usr/local/pgplot
cd /usr/local/pgplot
```

Copy the drivers list file:

`sudo cp /usr/local/src/pgplot/drivers.list .`

And edit it to enable /XWINDOW and /PNG, by removing the ! Or use mine:

```
sudo mv drivers.list drivers.list.backup
sudo wget https://raw.githubusercontent.com/EelkeVisser/stvid/master/readme/drivers.list
```

Generate the makefile.

`sudo /usr/local/src/pgplot/makemake /usr/local/src/pgplot linux f77_gcc`

This should result in:

```
For additional information, read file /usr/local/src/pgplot/sys_linux/aaaread.me
Reading configuration file: /usr/local/src/pgplot/sys_linux/f77_gcc.conf
Selecting uncommented drivers from ./drivers.list
Found drivers NUDRIV PNDRIV XWDRIV
Copying color database.
Creating make file: makefile
Determining object file dependencies.
```

You should have the following files, when running `ls -l`:

```
total 128
-rw-r--r-- 1 root root  6577 Jan  7 21:02 drivers.list
-rw-r--r-- 1 root root  6577 Jan  7 21:01 drivers.list.backup
-rw-r--r-- 1 root root   750 Jan  7 21:02 grexec.f
-rw-r--r-- 1 root root  3911 Jan  7 21:02 grpckg1.inc
-rw-r--r-- 1 root root 40893 Jan  7 21:03 makefile
-rw-r--r-- 1 root root 40731 Jan  7 21:02 makefile.backup
-rw-r--r-- 1 root root  6287 Jan  7 21:02 pgplot.inc
-rw-r--r-- 1 root root 16059 Jan  7 21:02 rgb.txt

```

Now the makefile needs some editing. Or download mine:

```
sudo mv makefile makefile.backup
sudo wget https://raw.githubusercontent.com/EelkeVisser/stvid/master/readme/makefile
```

Remove -u at:

`FFLAGC=`

Change png to png14:

```
PGPLOT_LIB=-L`pwd` -lpgplot -lpng14 -lz
CPGPLOT_LIB=-L`pwd` -lcpgplot -lpgplot -lpng14 -lz

pndriv.o : /usr/local/include/libpng14/png.h /usr/local/include/libpng14/pngconf.h /usr/include/zlib.h /usr/include/zconf.h
```

Setup static linking of libpng14:

`SHARED_LIB_LIBS= -Wl,-Bstatic -L/usr/X11R6/lib -lX11 -lpng14 -lz -lg2c -Wl,-Bdynamic`

Now compile pgplot:

```

sudo make
sudo make clean
sudo make cpg
sudo ld -shared -o libcpgplot.so --whole-archive libcpgplot.a
sudo ld -shared -o libpgplot.so --whole-archive libpgplot.a
```

If all goes well, this leaves the compiled lib togheter with some demo programs in /usr/local/pgplot 

If you check the contents of this dir you should get `ls -l`:
```
total 4472
-rwxr-xr-x 1 root root 185060 Jan  7 21:10 cpgdemo
-rw-r--r-- 1 root root   6393 Jan  7 21:10 cpgplot.h
-rw-r--r-- 1 root root   6577 Jan  7 21:02 drivers.list
-rw-r--r-- 1 root root   6577 Jan  7 21:01 drivers.list.backup
-rw-r--r-- 1 root root    750 Jan  7 21:02 grexec.f
-rw-r--r-- 1 root root  66020 Jan  7 21:09 grfont.dat
-rw-r--r-- 1 root root   3911 Jan  7 21:02 grpckg1.inc
-rw-r--r-- 1 root root 110340 Jan  7 21:10 libcpgplot.a
-rwxr-xr-x 1 root root  27772 Jan  7 21:10 libcpgplot.so
-rw-r--r-- 1 root root 550670 Jan  7 21:09 libpgplot.a
-rwxr-xr-x 1 root root 306172 Jan  7 21:10 libpgplot.so
-rw-r--r-- 1 root root  40893 Jan  7 21:03 makefile
-rw-r--r-- 1 root root  40731 Jan  7 21:02 makefile.backup
-rwxr-xr-x 1 root root  22012 Jan  7 21:10 pgbind
-rwxr-xr-x 1 root root 228440 Jan  7 21:09 pgdemo1
-rwxr-xr-x 1 root root 160332 Jan  7 21:09 pgdemo10
-rwxr-xr-x 1 root root 155884 Jan  7 21:09 pgdemo11
-rwxr-xr-x 1 root root 150740 Jan  7 21:09 pgdemo12
-rwxr-xr-x 1 root root 233596 Jan  7 21:09 pgdemo13
-rwxr-xr-x 1 root root 148732 Jan  7 21:09 pgdemo14
-rwxr-xr-x 1 root root 173648 Jan  7 21:09 pgdemo15
-rwxr-xr-x 1 root root 161616 Jan  7 21:09 pgdemo16
-rwxr-xr-x 1 root root 169096 Jan  7 21:09 pgdemo17
-rwxr-xr-x 1 root root 180412 Jan  7 21:09 pgdemo2
-rwxr-xr-x 1 root root 196516 Jan  7 21:09 pgdemo3
-rwxr-xr-x 1 root root 188944 Jan  7 21:09 pgdemo4
-rwxr-xr-x 1 root root 164360 Jan  7 21:09 pgdemo5
-rwxr-xr-x 1 root root 155500 Jan  7 21:09 pgdemo6
-rwxr-xr-x 1 root root 155248 Jan  7 21:09 pgdemo7
-rwxr-xr-x 1 root root 124804 Jan  7 21:09 pgdemo8
-rwxr-xr-x 1 root root 168648 Jan  7 21:09 pgdemo9
-rw-r--r-- 1 root root 162651 Jan  7 21:09 pgplot.doc
-rw-r--r-- 1 root root   6287 Jan  7 21:02 pgplot.inc
-rwxr-xr-x 1 root root  33076 Jan  7 21:09 pgxwin_server
-rw-r--r-- 1 root root  16059 Jan  7 21:02 rgb.txt

```

If all goes well, this leaves the compiled lib togheter with some demo programs in /usr/local/pgplot Setup the environment variables:


```
PGPLOT_DIR="/usr/local/pgplot/"; export PGPLOT_DIR
PGPLOT_DEV=/xwindow; export PGPLOT_DEV
```

Run the demo programs to see if pgplot is working:

```
./pgdemo1
./cpgdemo
```

Should show:
![pgdemo1](./readme/pgdemo1.png)

Now you have a working pgplot in the folder /usr/local/pgplot but if you want to compile sattools, it can not find it. I solved this the ugly way by copying this whole dir to the include and library dir:
```
sudo cp * /usr/include -r
sudo cp * /usr/lib -r

```

### Sattools

See [https://github.com/cbassa/sattools](https://github.com/cbassa/sattools) for installation of sattools. Do not install pgplot5, as we already have it. Replace the installation of requirements with:

`sudo apt install git make dos2unix sextractor wcslib-dev libgsl-dev gfortran libpng-dev libx11-dev libjpeg-dev libexif-dev`


## Configuration
* Edit `configuration.ini` with your preferred settings. Especially [Common], [Credentials] and [Camera]: camera_type = PI. You may also want to experiment with the analog_gain and digital_gain settings.
* Make sure ST_DATADIR is set as an env variable pointing to the /data folder of sattools

## Running

Run acquire.py to start filming:
```
cd
cd stvid
./acquire.py -c /home/pi/stvid/configuration.ini 
```

You may want to add `-l` for a live view window. And for testing during daylight use `-t 120`, for a test of 120 seconds. 

For processing run:
```
cd /obs/20211225_0/203637
~/stvid/process.py -c ~/stvid/configuration.ini
```

## Todo

<details>

Features to be implemented.

#### High priority
* ~~Use sunset/sunrise times for starting/stopping data acquisition.~~
* ~~Automatic astrometric calibration.~~
* ~~Recognize unidentified satellite/meteor tracks using [3D Hough transform](http://www.ipol.im/pub/art/2017/208/).~~

#### Medium priority
* Pause data acquisition of the current line-of-sight (alt/az) is in the Earth's shadow for a particular orbital altitude.
* Investigate sensitivity loss of `significance=(max-mean)/sigma` if the four frame images are stored as 8bit integers instead of floats.


#### Low priority
* Implement python based star finding (stick with *source extractor* for now).
* Migrate to [python based SGP4/SDP4 algorithms](https://github.com/brandon-rhodes/python-sgp4)
* Use masks to mask unilluminated CCD areas.
* Investigate automatic submission of IOD measurements to [SeeSat-L](http://www.satobs.org/seesat/).
* ~~Migrate user settings to a configuration file.~~

## Run acquisition at startup

* Add user to video group (`sudo adduser <username> video`).
* Add video device to udev rules (add `SUBSYSTEM=="video1", GROUP="video", MODE="0660"` in `/etc/udev/rules.d/10-webcam.rules`).
* Create start up script in `/etc/init.d`. Call capture script as user with `su <username> -c "acquire.py"`.

</details>	
	
## License
&copy; 2018-2023 Cees Bassa

Licensed under the [GPLv3](LICENSE).
