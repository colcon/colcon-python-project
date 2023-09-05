# Copyright 2023 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import os

from colcon_core.argument_parser import ArgumentParserDecoratorExtensionPoint
from colcon_core.plugin_system import satisfies_version

try:
    from colcon_core.extension_point \
        import EXTENSION_BLOCKLIST_ENVIRONMENT_VARIABLE as BLOCK_VAR
except ImportError:
    from colcon_core.entry_point \
        import EXTENSION_BLOCKLIST_ENVIRONMENT_VARIABLE as BLOCK_VAR


class PythonProjectArgumentParserDecorator(
    ArgumentParserDecoratorExtensionPoint
):
    """Disable extensions which conflict with colcon-python-project."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            ArgumentParserDecoratorExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def decorate_argument_parser(self, *, parser):  # noqa: D102
        blocks = []
        if os.environ.get(BLOCK_VAR.name, None):
            blocks = os.environ[BLOCK_VAR.name].split(os.pathsep)

        if 'colcon_core.package_identification.python' not in blocks:
            blocks.append('colcon_core.package_identification.python')

        if 'colcon_core.package_identification.python_setup_py' not in blocks:
            blocks.append('colcon_core.package_identification.python_setup_py')

        os.environ[BLOCK_VAR.name] = os.pathsep.join(blocks)

        return parser
