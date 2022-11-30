# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from colcon_python_project.hook_caller import AsyncHookCaller
import pytest

_BACKEND_NAME = 'setuptools.build_meta:__legacy__'


@pytest.fixture
def mock_project(tmp_path):
    with (tmp_path / 'test_project.py').open('w'):
        pass
    with (tmp_path / 'README').open('w'):
        pass
    with (tmp_path / 'setup.cfg').open('w') as f:
        f.write('\n'.join([
            '[metadata]',
            'name = test-project',
            '[options]',
            'packages = find:',
        ]))
    with (tmp_path / 'setup.py').open('w') as f:
        f.write('\n'.join([
            'from setuptools import setup',
            'setup()',
        ]))
    with (tmp_path / 'pyproject.toml').open('w') as f:
        f.write('\n'.join([
            '[build-system]',
            'requires = ["setuptools>=40.8.0"]',
            f'build-backend = "{_BACKEND_NAME}"',
        ]))
    yield tmp_path


@pytest.mark.asyncio
async def test_build_wheel(mock_project, tmp_path):
    hook_caller = AsyncHookCaller(
        _BACKEND_NAME, project_path=mock_project)
    wheel = await hook_caller.build_wheel(wheel_directory=str(tmp_path))
    assert isinstance(wheel, str)
    assert (tmp_path / wheel).is_file()


@pytest.mark.asyncio
async def test_build_sdist(mock_project, tmp_path):
    hook_caller = AsyncHookCaller(
        _BACKEND_NAME, project_path=mock_project)
    sdist = await hook_caller.build_sdist(sdist_directory=str(tmp_path))
    assert isinstance(sdist, str)
    assert (tmp_path / sdist).is_file()


@pytest.mark.asyncio
async def test_get_requires_for_build_wheel(mock_project):
    hook_caller = AsyncHookCaller(
        _BACKEND_NAME, project_path=mock_project)
    requires = await hook_caller.get_requires_for_build_wheel()
    assert isinstance(requires, list)


@pytest.mark.asyncio
async def test_prepare_metadata_for_build_wheel(mock_project, tmp_path):
    hook_caller = AsyncHookCaller(
        _BACKEND_NAME, project_path=mock_project)
    distinfo = await hook_caller.prepare_metadata_for_build_wheel(
        metadata_directory=str(tmp_path))
    assert isinstance(distinfo, str)
    assert (tmp_path / distinfo).is_dir()


@pytest.mark.asyncio
async def test_get_requires_for_build_sdist(mock_project):
    hook_caller = AsyncHookCaller(
        _BACKEND_NAME, project_path=mock_project)
    requires = await hook_caller.get_requires_for_build_sdist()
    assert isinstance(requires, list)


@pytest.mark.asyncio
@pytest.mark.skip(reason='Insufficient setuptools version')
async def test_build_editable(mock_project, tmp_path):
    hook_caller = AsyncHookCaller(
        _BACKEND_NAME, project_path=mock_project)
    wheel = await hook_caller.build_editable(
        wheel_directory=str(tmp_path))
    assert isinstance(wheel, str)
    assert (tmp_path / wheel).is_file()


@pytest.mark.asyncio
@pytest.mark.skip(reason='Insufficient setuptools version')
async def test_get_requires_for_build_editable(mock_project):
    hook_caller = AsyncHookCaller(
        _BACKEND_NAME, project_path=mock_project)
    requires = await hook_caller.get_requires_for_build_editable()
    assert isinstance(requires, list)


@pytest.mark.asyncio
@pytest.mark.skip(reason='Insufficient setuptools version')
async def test_prepare_metadata_for_build_editable(mock_project, tmp_path):
    hook_caller = AsyncHookCaller(
        _BACKEND_NAME, project_path=mock_project)
    dist_info = await hook_caller.prepare_metadata_for_build_editable(
        metadata_directory=str(tmp_path))
    assert isinstance(dist_info, str)
    assert (tmp_path / dist_info).is_dir()
