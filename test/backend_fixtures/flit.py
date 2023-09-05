# Copyright 2023 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import pytest


@pytest.fixture
def mock_backend_project(mock_desc):
    with (mock_desc.path / 'pyproject.toml').open('w') as f:
        f.write('\n'.join([
            '[build-system]',
            'requires = ["flit_core >=3.2,<4"]',
            'build-backend = "flit_core.buildapi"',
            '',
            '[project]',
            f'name = "{mock_desc.name}"',
            'version = "0.0.0"',
            'description = "A test project"',
            '',
            '[tool.flit.module]',
            'name = "test_project"',
        ]))
    return mock_desc
