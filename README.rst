colcon-python-project
=====================

Extensions for `colcon-core <https://github.com/colcon/colcon-core>`_ to work with Python packages which use a ``pyproject.toml`` file.

**:warning: This is a prototype package, and isn't ready for widespread use.**
**Please continue using the Python package support in** ``colcon-core`` **and** ``colcon-python-setup-py`` **until these extensions are ready.**

TODO
----
* Graceful and informational error handling

Idiosyncrasies
--------------
* For setuptools-based packages, setuptools (< 64.0.0) will leave build artifacts in the source directory.
* For setuptools-based packages, symlink installs always print warnings to stderr with no good way to suppress them.
* For poetry-based packages, dependencies expressed in groups (including 'test') are not discovered (use 'test' extra as a workaround).

Using This Prototype
--------------------
* To build PEP 517 projects which don't have a ``setup.py`` file, simply install this package as any other colcon extension package.
* To build legacy ``setup.py`` projects using this package instead of the existing python extensions in ``colcon-core`` and ``colcon-python-setup-py``, use the ``COLCON_EXTENSION_BLOCKLIST`` to block them and this package will discover them as a fallback (see `pep517_setuptools_fallback documentation <https://github.com/colcon/colcon-python-project/blob/devel/colcon_python_project/package_identification/pep517_setuptools_fallback.py>`_).
* To build ``ament_python`` projects using the extensions in this package, use the `colcon-python-project branch <https://github.com/colcon/colcon-ros/tree/colcon-python-project>`_ of ``colcon-ros``.
