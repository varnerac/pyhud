# pyhud

Python-based HUD for Minisim

## Installation

Download the latest version of Python 2.7. Currently, this is Python 2.7.14. It can be found at [python.org](https://www.python.org/downloads/)

Install the playsound library by typing the following at the command prompt or terminal.

```
pip install playsound
```

Download the Zip file [here](https://github.com/varnerac/pyhud/archive/master.zip)

Unzip and install it somewhere in your user directory

Go to where you installed the package and type the following to run it in default mode, which is visual and stereo audio cues:

```
python pyhud.py
```

For information on options, including:

* visual-only mode
* audio-only mode
* mono audio mode

type:

```
pyhud varnerac$ python pyhud.py -h
usage: pyhud.py [-h] [--disable-audio] [--disable-visual] [--mono-audio]
Run the Heads-Up Display (HUD)
optional arguments:
  -h, --help        show this help message and exit
  --disable-audio   disable audio cues
  --disable-visual  disable visual cues
  --mono-audio      use mono audio cues
```
