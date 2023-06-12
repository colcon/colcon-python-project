colcon-python-project
=====================

Extensions for `colcon-core <https://github.com/colcon/colcon-core>`_ to work with Python packages which use a ``pyproject.toml`` file.

**:warning: This is a prototype package, and isn't ready for widespread use.**
**Please continue using the Python package support in** ``colcon-core`` **and** ``colcon-python-setup-py`` **until these extensions are ready.**

TODO
----
* Graceful and informational error handling
* More tests

Idiosyncrasies
--------------
* For setuptools-based packages, setuptools (< 64.0.0) will leave build artifacts in the source directory.
* For setuptools-based packages, symlink installs always print warnings to stderr with no good way to suppress them.
* For poetry-based packages, dependencies expressed in groups (including 'test') are not discovered (use 'test' extra as a workaround).

Using This Prototype
--------------------

   $ mkdir -p ~/colcon_pyproject_ws/src && cd ~/colcon_pyproject_ws
   $ git clone https://github.com/colcon/colcon-python-project.git -b devel src/colcon-python-project
   $ colcon build
   $ . install/local_setup.sh
