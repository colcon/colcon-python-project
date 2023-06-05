# Copyright 2023 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from colcon_core.package_augmentation import PackageAugmentationExtensionPoint
from colcon_core.plugin_system import satisfies_version


class RosAmentPythonProjectPackageAugmentation(
    PackageAugmentationExtensionPoint
):
    """Convert ament_python packages to ament_python.project."""

    # Allow other augmentation extensions to perform normally and only change
    # the type at the end to allow the correct build extension to be invoked.
    PRIORITY = 999

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageAugmentationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def augment_package(  # noqa: D102
        self, desc, *, additional_argument_names=None
    ):
        if desc.type != 'ros.ament_python':
            return

        desc.type += '.project'
