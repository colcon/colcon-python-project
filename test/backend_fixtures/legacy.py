# Copyright 2023 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import pytest


@pytest.fixture
def mock_backend_project(mock_desc):
    with (mock_desc.path / 'setup.cfg').open('w') as f:
        f.write('\n'.join([
            '[metadata]',
            f'name = {mock_desc.name}',
            '[options]',
            'packages = find:',
        ]))
    with (mock_desc.path / 'setup.py').open('w') as f:
        f.write('\n'.join([
            'from setuptools import setup',
            'setup()',
        ]))
    with (mock_desc.path / 'pyproject.toml').open('w') as f:
        f.write('\n'.join([
            '[build-system]',
            'requires = ["setuptools>=40.8.0"]',
            'build-backend = "setuptools.build_meta:__legacy__"',
        ]))
    return mock_desc
