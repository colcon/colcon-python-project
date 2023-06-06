# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import logging
from subprocess import CalledProcessError

from colcon_core.logging import colcon_logger
from colcon_core.package_identification \
    import PackageIdentificationExtensionPoint
from colcon_core.plugin_system import satisfies_version
from colcon_core.subprocess import new_event_loop
from colcon_python_project.metadata import load_and_cache_metadata
from colcon_python_project.spec import SPEC_NAME

logger = colcon_logger.getChild(__name__)


class PEP517PackageIdentification(PackageIdentificationExtensionPoint):
    """
    Identify Python packages with `pyproject.toml` using the build backend.

    This mechanism is very slow compared with other identification extensions.
    It should be able to function with any PEP 517 compliant build backend,
    but those backends which see widespread use should implement a more
    efficient identification extension.
    """

    # the priority needs to be higher than the extensions identifying packages
    # using setup.py and/or setup.cfg files but lower than other more efficient
    # PEP 517 compliant identification extensions.
    PRIORITY = 110

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

        # avoid debug message from asyncio when colcon uses debug log level
        asyncio_logger = logging.getLogger('asyncio')
        asyncio_logger.setLevel(logging.INFO)

    def identify(self, desc):  # noqa: D102
        if desc.type is not None and desc.type != 'python.project':
            return

        if desc.type is None:
            spec_file = desc.path / SPEC_NAME
            if not spec_file.is_file():
                return

        loop = new_event_loop()
        try:
            metadata = loop.run_until_complete(
                load_and_cache_metadata(desc))
        except CalledProcessError as e:
            logger.warn(
                f'An error occurred while reading metadata for {desc.path}:'
                f" {e.stderr.strip().decode() or '(no output)'}")
            return
        finally:
            loop.stop()
            loop.close()
        name = metadata.get('Name')
        if not name:
            return

        desc.name = name
        desc.type = 'python.project'
