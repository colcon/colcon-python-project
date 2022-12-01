# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

try:
    from tomllib import load as toml_load
except ImportError:
    from tomli import load as toml_load


SPEC_NAME = 'pyproject.toml'

_DEFAULT_BUILD_SYSTEM = {
    'build-backend': 'setuptools.build_meta:__legacy__',
    'requires': ['setuptools >= 40.8.0', 'wheel'],
}


def load_spec(project_path):
    """
    Load build system specifications for a Python project.

    :param project_path: Path to the root directory of the project
    """
    spec_file = project_path / SPEC_NAME
    try:
        with spec_file.open('rb') as f:
            spec = toml_load(f)
    except FileNotFoundError:
        spec = {}

    spec.setdefault('build-system', _DEFAULT_BUILD_SYSTEM)

    return spec


def load_and_cache_spec(desc):
    """
    Get the cached spec for a package descriptor.

    If the spec has not been loaded yet, load and cache it.

    :param desc: The package descriptor
    """
    spec = desc.metadata.get('python_project_spec')
    if spec is None:
        spec = load_spec(desc.path)
        desc.metadata['python_project_spec'] = spec
    return spec