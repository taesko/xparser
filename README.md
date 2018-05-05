XParser
=======
A very simple python library for parsing XResources.

### Example Usage
```python
import xrp
result = xrp.parse_file('.Xresources')
result.resources['*foreground'] == '#FFFFFF'
result.resources.x_statement('*foreground').value == 'white'
result.definitions['white'] == '#FFFFFF'
```

### Installation
Install stable versions from PyPi

```bash
pip install xparser
``` 

and development versions by cloning

```bash
git clone https://github.com/taesko/xparser.git
cd xparser && pip install .
```

### Documentation
The two main entry points to the API are the `parse` and `parse_file` functions in the `xrp` package

They both return an xrp.views.XFileView object, which has `resources` and `definitions` attributes with
dict-like interface for accessing the parsed data.

No designated docs are written yet (but are planned to be) - use help() on the xrp.views.XFileView object
for more information on usage.
