# pyjacknet

## What is pyjacknet

pyjacknet is a utility for sending monodirectional audio through network. The audio communication with the machine relies on [JACK (Jack Audio Connection Kit)](https://jackaudio.org/) and it supports mono and stereo signals. Data can be sent uncompressed (32bit floating point per sample), compressed as 16bit integer per sample (CD quality) or compressed as [opus](https://opus-codec.org/) stream.

## What is not pyjacknet

pyjacknet is not a utility for professional nor stable streaming. It started as a simple project that "reinvents the wheel" just as a study case, and if you need to stream audio you should check [real projects](https://jackaudio.org/faq/netjack.html). If you need real time requirements you may not want to use python, as I said this started as a study case. It is also meant to be run in linux and is currently in development stage.

## How it works

pyjacknet uses tcp/ip sockets and consists of two command-line software:

- pyjacknet_client:  the tcp/ip client, it receives audio from JACK and sends it to the server. It has only input ports.
- pyjacknet_server: the tcp/ip server, it receives audio from the connected client and sends it to JACK. It has only output ports.

In order to work, the server must be reacheable by the client and is currently untested (but it may work if connection is stable) in a wide area network. No security features are currently available.

The same sample rate should be set in both client and server. There is no feature to correct "sample rate drifting" in the long run.

## Requirements

Since pyjacknet relies send and receive audio via JACK you need to have JACK installed on your system.

pyjacknet requires python3 in order to work. It uses the [jackclient](https://github.com/spatialaudio/jackclient-python) library from spatialaudio. Data are handled using [numpy](https://numpy.org/) so it is also necessary to install numpy. These packages are installed automatically if using pip.

The last requirement is optional and needed only if you want to use opus compression: the [PyOgg](https://github.com/TeamPyOgg/PyOgg) from TeamPyOgg, it can be installed via pip using

    pip install git+https://github.com/TeamPyOgg/PyOgg

N.B. At the moment (January 2021) the PyPI package of PyOgg is too old so to use the features required by pyjacknet you have to install the latest version on the git repo. This may change in the near future.

## Installation

If all dependencies are installed you can execute the package pyjacknet.

If instead you want to install pyjacknet you have first to build with a pep517 compliant installer. If you use the [pep517](https://github.com/pypa/pep517) package, execute this command inside the project folder:

    python -m pep517.build .

You will have the distribution files inside the dist folder that are ready to be installed via pip.

## Usage

TODO

## License

This project is licensed under the MIT License - see LICENSE file for details.

pyjacknet - Copyright (C) 2021 Brilli Lorenzo