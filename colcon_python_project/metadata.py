# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from pathlib import Path
from tempfile import TemporaryDirectory

from colcon_python_project.hook_caller_decorator \
    import get_decorated_hook_caller

try:
    from importlib.metadata import Distribution
except ImportError:
    from importlib_metadata import Distribution


async def load_metadata(desc):
    """
    Load metadata for a Python project using PEP 517.

    :param desc: The package descriptor
    """
    hook_caller = get_decorated_hook_caller(desc)
    with TemporaryDirectory() as md_dir:
        md_name = await hook_caller.prepare_metadata_for_build_wheel(
            metadata_directory=md_dir)
        md_path = Path(md_dir) / md_name
        return Distribution.at(md_path).metadata


async def load_and_cache_metadata(desc):
    """
    Get the cached metadata for a package descriptor.

    If the metadata has not been loaded yet, load and cache it.

    :param desc: The package descriptor
    """
    get_metadata = desc.metadata.get('get_python_project_metadata')
    if get_metadata is None:
        metadata = await load_metadata(desc)

        def get_metadata():
            return metadata

        desc.metadata['get_python_project_metadata'] = get_metadata
    return get_metadata()
