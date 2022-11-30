colcon-python-project
=====================

Extensions for `colcon-core <https://github.com/colcon/colcon-core>`_ to work with Python packages which use a ``pyproject.toml`` file.

**:warning: This is a prototype package, and isn't ready for widespread use.**
**Please continue using the Python package support in** ``colcon-core`` **and** ``colcon-python-setup-py`` **until these extensions are ready.**

TODO
----
* Install RECORD file
* Graceful and informational error handling
* Finish PEP 660 (symlink) installs

Idiosyncrasies
--------------
* For setuptools-based packages, setuptools (< 64.0.0) will leave build artifacts in the source directory.
* For poetry-based packages, dependencies expressed in groups (including 'test') are not discovered (use 'test' extra as a workaround).
