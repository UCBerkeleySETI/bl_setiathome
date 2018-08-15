## requant_utils

Tools for requantization of radio astronomy data. Currently only supports 8-bit integer to 2-bit data.

Project built with [pybind11](https://github.com/pybind/pybind11).

### Installation

**On Unix (Linux, OS X)**

 - clone this repository
 - `python setup.py build_ext -i` to build shared object .so locally, or
 - `python setup.py install` to install globally

### Test call

```python
imoprt numpy as np
import requant_utils
a = np.array([-3, -2, -1, 0, 1, 2, 3, 4], dtype='int8')
b = np.zeros(a.shape[0]/4, dtype='uint8')

requant_utils.requant_8i_2u(a, b)
```
