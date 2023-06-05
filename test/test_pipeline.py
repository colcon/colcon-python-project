# Copyright 2023 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from copy import deepcopy

from colcon_core.package_augmentation.python \
    import PythonPackageAugmentation
from colcon_core.package_descriptor import PackageDescriptor
from colcon_core.package_identification.python \
    import PythonPackageIdentification
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
            PEP517PackageAugmentation())
        for backend in MOCK_BACKENDS
    },
    'pep517.setuptools_fallback': (
        'legacy',
        PEP517SetuptoolsFallbackPackageIdentification(),
        PEP517PackageAugmentation()),
    'pep621': (
        'flit',
        PEP621PackageIdentification(),
        PEP621PackageAugmentation()),
    'setup_cfg': (
        'legacy',
        PythonPackageIdentification(),
        PythonPackageAugmentation()),
    'setup_py': (
        'legacy',
        SetupPyPackageIdentification(),
        SetupPyPackageAugmentation()),
}


@pytest.mark.benchmark(group='pipeline.package_identification')
@pytest.mark.parametrize(
    'backend,identifier,_',
    PIPELINES.values(),
    ids=PIPELINES.keys())
def test_identify(backend, identifier, _, request, benchmark):
    mock_project = request.getfixturevalue(f'mock_{backend}_project')

    def dut():
        mock_desc = PackageDescriptor(mock_project.path)
        assert identifier.identify(mock_desc) is None
        return mock_desc
    mock_desc = benchmark(dut)
    assert mock_desc.identifies_package()


@pytest.mark.benchmark(group='pipeline.package_augmentation')
@pytest.mark.parametrize(
    'backend,identifier,augmentor',
    PIPELINES.values(),
    ids=PIPELINES.keys())
def test_augment(backend, identifier, augmentor, request, benchmark):
    mock_project = request.getfixturevalue(f'mock_{backend}_project')
    mock_project = PackageDescriptor(mock_project.path)
    assert identifier.identify(mock_project) is None
    assert mock_project.identifies_package()

    @benchmark
    def dut():
        mock_desc = deepcopy(mock_project)
        assert augmentor.augment_package(mock_desc) is None
