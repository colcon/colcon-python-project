# Copyright 2023 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from copy import deepcopy
import os
from types import SimpleNamespace
from unittest.mock import patch

from colcon_core.package_augmentation.python \
    import PythonPackageAugmentation
from colcon_core.package_descriptor import PackageDescriptor
from colcon_core.package_identification.python \
    import PythonPackageIdentification
from colcon_core.shell import ShellExtensionPoint
from colcon_core.task import TaskContext
from colcon_core.task.python.build import PythonBuildTask
from colcon_python_project.package_augmentation.pep517 \
    import PEP517PackageAugmentation
from colcon_python_project.package_augmentation.pep621 \
    import PEP621PackageAugmentation
from colcon_python_project.package_identification.pep517 \
    import PEP517PackageIdentification
from colcon_python_project.package_identification.pep517_setuptools_fallback \
    import PEP517SetuptoolsFallbackPackageIdentification
from colcon_python_project.package_identification.pep621 \
    import PEP621PackageIdentification
from colcon_python_project.task.python.project.build \
    import PythonProjectBuildTask
from colcon_python_setup_py.package_augmentation.python_setup_py \
    import PythonPackageAugmentation as SetupPyPackageAugmentation
from colcon_python_setup_py.package_identification.python_setup_py \
    import PythonPackageIdentification as SetupPyPackageIdentification
import pytest

from .conftest import MOCK_BACKENDS


PIPELINES = {
    **{
        f'pep517.{backend}': (
            backend,
            PEP517PackageIdentification(),
            PEP517PackageAugmentation(),
            PythonProjectBuildTask())
        for backend in MOCK_BACKENDS
    },
    'pep517.setuptools_fallback': (
        'legacy',
        PEP517SetuptoolsFallbackPackageIdentification(),
        PEP517PackageAugmentation(),
        PythonProjectBuildTask()),
    'pep621': (
        'flit',
        PEP621PackageIdentification(),
        PEP621PackageAugmentation(),
        PythonProjectBuildTask()),
    'setup_cfg': (
        'legacy',
        PythonPackageIdentification(),
        PythonPackageAugmentation(),
        PythonBuildTask()),
    'setup_py': (
        'legacy',
        SetupPyPackageIdentification(),
        SetupPyPackageAugmentation(),
        PythonBuildTask()),
}


class _NoEventsTaskContext(TaskContext):

    def put_event_into_queue(self, event):
        pass


class _NoopShellExtension(ShellExtensionPoint):

    PRIORITY = 200

    SHELL_NAME = 'noop'

    def create_prefix_script(self, prefix_path, merge_install):
        return []

    def create_package_script(self, prefix_path, pkg_name, hooks):
        return []

    def create_hook_set_value(
        self, env_hook_name, prefix_path, pkg_name, name, value,
    ):
        hook_file = \
            prefix_path / 'share' / pkg_name / 'hook' / f'{env_hook_name}.noop'
        hook_file.parent.mkdir(parents=True, exist_ok=True)
        hook_file.write_text('')
        return hook_file

    def create_hook_append_value(
        self, env_hook_name, prefix_path, pkg_name, name, subdirectory,
    ):
        hook_file = \
            prefix_path / 'share' / pkg_name / 'hook' / f'{env_hook_name}.noop'
        hook_file.parent.mkdir(parents=True, exist_ok=True)
        hook_file.write_text('')
        return hook_file

    def create_hook_prepend_value(
        self, env_hook_name, prefix_path, pkg_name, name, subdirectory,
    ):
        hook_file = \
            prefix_path / 'share' / pkg_name / 'hook' / f'{env_hook_name}.noop'
        hook_file.parent.mkdir(parents=True, exist_ok=True)
        hook_file.write_text('')
        return hook_file

    def create_hook_include_file(
        self, env_hook_name, prefix_path, pkg_name, relative_path,
    ):
        hook_file = \
            prefix_path / 'share' / pkg_name / 'hook' / f'{env_hook_name}.noop'
        hook_file.parent.mkdir(parents=True, exist_ok=True)
        hook_file.write_text('')
        return hook_file

    async def generate_command_environment(
        self, task_name, build_base, dependencies,
    ):
        return dict(os.environ)


@pytest.fixture(autouse=True, scope='module')
def suppress_shell_extensions():
    with patch(
        'colcon_core.shell.get_shell_extensions',
        return_value={
            _NoopShellExtension.PRIORITY: {
                _NoopShellExtension.SHELL_NAME: _NoopShellExtension()
            },
        },
    ):
        yield


@pytest.mark.benchmark(group='pipeline.package_identification')
@pytest.mark.parametrize(
    'backend,identifier,_,__',
    PIPELINES.values(),
    ids=PIPELINES.keys())
def test_identify(backend, identifier, _, __, request, benchmark):
    mock_project = request.getfixturevalue(f'mock_{backend}_project')

    def dut():
        mock_desc = PackageDescriptor(mock_project.path)
        assert identifier.identify(mock_desc) is None
        return mock_desc
    mock_desc = benchmark(dut)
    assert mock_desc.identifies_package()


@pytest.mark.benchmark(group='pipeline.package_augmentation')
@pytest.mark.parametrize(
    'backend,identifier,augmentor,_',
    PIPELINES.values(),
    ids=PIPELINES.keys())
def test_augment(backend, identifier, augmentor, _, request, benchmark):
    mock_project = request.getfixturevalue(f'mock_{backend}_project')
    mock_project = PackageDescriptor(mock_project.path)
    assert identifier.identify(mock_project) is None
    assert mock_project.identifies_package()

    @benchmark
    def dut():
        mock_desc = deepcopy(mock_project)
        assert augmentor.augment_package(mock_desc) is None


@pytest.mark.benchmark(group='pipeline.build')
@pytest.mark.parametrize(
    'backend,identifier,augmentor,build_task',
    PIPELINES.values(),
    ids=PIPELINES.keys())
def test_build(
    backend, identifier, augmentor, build_task, request, bench,
    tmp_path_factory
):
    mock_project = request.getfixturevalue(f'mock_{backend}_project')
    mock_project = PackageDescriptor(mock_project.path)
    assert identifier.identify(mock_project) is None
    assert mock_project.identifies_package()
    assert augmentor.augment_package(mock_project) is None

    async def dut():
        build_task.set_context(context=_NoEventsTaskContext(
            pkg=mock_project,
            args=SimpleNamespace(
                path=str(mock_project.path),
                build_base=str(tmp_path_factory.mktemp('build')),
                install_base=str(tmp_path_factory.mktemp('install')),
                symlink_install=False,
            ),
            dependencies={},
        ))

        return await build_task.build()

    assert not bench(dut)
