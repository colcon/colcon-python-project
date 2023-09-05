# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from colcon_python_project.package_identification.pep517 \
    import PEP517PackageIdentification


class PEP517SetuptoolsFallbackPackageIdentification(
    PEP517PackageIdentification
):
    """
    Identify legacy setuptools packages using PEP 517.

    To use this extension, disable the ``python`` and ``python_setup_py``
    identification extensions using this environment variable:
    ``COLCON_EXTENSION_BLOCKLIST=colcon_core.package_identification.python:colcon_core.package_identification.python_setup_py``
    """

    # the priority needs to be lower than all other Python package
    # identification extensions.
    PRIORITY = 80

    def identify(self, desc):  # noqa: D102
        if desc.type is not None and desc.type != 'python.project':
            return

        setup_cfg_file = desc.path / 'setup.cfg'
        setup_py_file = desc.path / 'setup.py'

        if not setup_cfg_file.is_file() and not setup_py_file.is_file():
            return

        if desc.type is not None:
            return super().identify(desc)

        desc.type = 'python.project'
        try:
            return super().identify(desc)
        finally:
            if not desc.name:
                desc.type = None
