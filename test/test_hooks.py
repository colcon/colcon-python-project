# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import os
import sys

from colcon_python_project.hook_caller_decorator \
    import get_decorated_hook_caller
import pytest


@pytest.fixture
def mock_hook_caller(mock_project):
    env = {
        **os.environ,
        'PYTHONWARNINGS': 'ignore',
    }
    return get_decorated_hook_caller(
        mock_project,
        env=env, stderr_callback=sys.stderr.buffer.write)


@pytest.mark.benchmark(group='hooks.build_wheel')
def test_build_wheel(mock_hook_caller, tmp_path_factory, bench):
    async def dut():
        out = tmp_path_factory.mktemp('out')
        return out / await mock_hook_caller.build_wheel(
           wheel_directory=str(out))
    wheel = bench(dut)
    assert wheel.is_file()


@pytest.mark.benchmark(group='hooks.build_sdist')
def test_build_sdist(mock_hook_caller, tmp_path_factory, bench):
    async def dut():
        out = tmp_path_factory.mktemp('out')
        return out / await mock_hook_caller.build_sdist(
            sdist_directory=str(out))
    sdist = bench(dut)
    assert sdist.is_file()


@pytest.mark.benchmark(group='hooks.get_requires_for_build_wheel')
def test_get_requires_for_build_wheel(mock_hook_caller, bench):
    requires = bench(mock_hook_caller.get_requires_for_build_wheel)
    assert isinstance(requires, list)


@pytest.mark.benchmark(group='hooks.prepare_metadata_for_build_wheel')
def test_prepare_metadata_for_build_wheel(
    mock_hook_caller, tmp_path_factory, bench
):
    async def dut():
        out = tmp_path_factory.mktemp('out')
        return out / await mock_hook_caller.prepare_metadata_for_build_wheel(
            metadata_directory=str(out))
    dist_info = bench(dut)
    assert dist_info.is_dir()


@pytest.mark.benchmark(group='hooks.get_requires_for_build_sdist')
def test_get_requires_for_build_sdist(mock_hook_caller, bench):
    requires = bench(mock_hook_caller.get_requires_for_build_sdist)
    assert isinstance(requires, list)


@pytest.mark.benchmark(group='hooks.build_editable')
def test_build_editable(mock_hook_caller, tmp_path_factory, bench):
    async def dut():
        out = tmp_path_factory.mktemp('out')
        return out / await mock_hook_caller.build_editable(
            wheel_directory=str(out))
    wheel = bench(dut)
    assert wheel.is_file()


@pytest.mark.benchmark(group='hooks.get_requires_for_build_editable')
def test_get_requires_for_build_editable(mock_hook_caller, bench):
    requires = bench(mock_hook_caller.get_requires_for_build_editable)
    assert isinstance(requires, list)


@pytest.mark.benchmark(group='hooks.prepare_metadata_for_build_editable')
def test_prepare_metadata_for_build_editable(
    mock_hook_caller, tmp_path_factory, bench
):
    async def dut():
        out = tmp_path_factory.mktemp('out')
        return out / \
            await mock_hook_caller.prepare_metadata_for_build_editable(
                metadata_directory=str(out))
    dist_info = bench(dut)
    assert dist_info.is_dir()


@pytest.mark.benchmark(group='hooks.list_hooks')
def test_list_hooks(mock_hook_caller, bench):
    hook_names = bench(mock_hook_caller.list_hooks)
    assert isinstance(hook_names, list)
    assert 'build_sdist' in hook_names
    assert 'build_wheel' in hook_names
