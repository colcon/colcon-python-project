# Copyright 2023 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import logging
import os
import unittest.mock
import warnings

from colcon_core.package_descriptor import PackageDescriptor
from colcon_python_project.hook_caller_decorator.setuptools \
    import SetuptoolsHookCallerDecoratorExtension
import pytest

from .backend_fixtures import *  # noqa: F401, F403
from .backend_fixtures import MOCK_BACKENDS


@pytest.fixture(autouse=True)
def better_benchmarking(request):
    if 'benchmark' not in request.fixturenames:
        yield
        return
    benchmark = request.getfixturevalue('benchmark')
    if not benchmark.enabled:
        yield
        return
    if 'COV_CORE_DATAFILE' in os.environ:
        warnings.warn(
            "Can't run benchmarks with coverage enabled. "
            'Re-run with --no-cov.')
        benchmark.disabled = True
        yield
        return
    logging.disable(level=logging.ERROR)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        yield
    logging.disable(level=logging.NOTSET)


@pytest.fixture(autouse=True, scope='session')
def static_extensions():
    def override_extensions(group_name, *args, **kwargs):
        if group_name == 'colcon_python_project.hook_caller_decorator':
            return {
                'setuptools': SetuptoolsHookCallerDecoratorExtension(),
            }
        return unittest.mock.DEFAULT

    with unittest.mock.patch(
        'colcon_python_project.hook_caller_decorator.instantiate_extensions',
        side_effect=override_extensions,
    ) as p:
        yield p


@pytest.fixture
def bench(benchmark, event_loop):
    def res(target, *args, **kwargs):
        def dut():
            return event_loop.run_until_complete(target(*args, **kwargs))
        return benchmark(dut)
    return res


@pytest.fixture
def mock_desc(tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    with (src / 'test_project.py').open('w'):
        pass
    with (src / 'README').open('w'):
        pass
    desc = PackageDescriptor(src)
    desc.name = 'test-project'
    desc.type = 'python.project'
    return desc


@pytest.fixture(params=MOCK_BACKENDS)
def mock_project(request):
    return request.getfixturevalue(f'mock_{request.param}_project')
