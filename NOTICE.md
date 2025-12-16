# Third-Party Notices and License Attribution

This project is licensed under the MIT License. See `LICENSE`.

This distribution includes or interoperates with third-party components. Their licenses and attributions are preserved below or referenced for compliance.

## Project Attribution

- File `src/denkovi_relayboard/hid/__init__.py` is adapted from work by Austin Morton and is licensed under the MIT License. Local modifications adjust dynamic library search behavior to improve cross-platform loading of `hidapi` shared libraries.

## Bundled Binary

- `libhidapi-hidraw.so` is bundled from Debian’s `libhidapi-hidraw0` package.  
  - Upstream project: HIDAPI (`https://github.com/libusb/hidapi`)  
  - Debian package reference: `https://packages.debian.org/trixie/libhidapi-hidraw0`  
  - License selection: HIDAPI offers a multi-license model; this distribution follows the BSD-Style license. See upstream LICENSE files.

## Python Dependencies

- `pyserial` (BSD-3-Clause)  
  - Project: `https://github.com/pyserial/pyserial`  
  - License: `https://pypi.org/project/pyserial/`

- `pyftdi` (BSD-3-Clause)  
  - Project: `https://github.com/eblot/pyftdi`  
  - License: `https://github.com/conda-forge/pyftdi-feedstock`

- `typing_extensions` (PSF-2.0)  
  - Project: `https://github.com/python/typing_extensions`  
  - License: `https://github.com/python/typing_extensions/blob/main/LICENSE`

## HIDAPI BSD-Style License (Text)

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the project nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
