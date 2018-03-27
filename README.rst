=======
XParser
=======
A very simple python library for parsing XResources.

-------------
Example Usage
-------------
.. code:: python

    import xrp
    result = xrp.parse_file('.Xresources')
    result.resources['*foreground'] == 'white'
    result.definitions['white'] == '#FFFFFF'

------------
Installation
------------
Install stable versions from PyPi

.. code:: bash

    pip install xparser

and development versions by cloning

.. code:: bash

    git clone https://github.com/taesko/xparser.git
    cd xparser && pip install .

-------------
Documentation
-------------
is not (yet) written.
