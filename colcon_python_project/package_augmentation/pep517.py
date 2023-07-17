# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

import asyncio
import logging
from subprocess import CalledProcessError

from colcon_core.logging import colcon_logger
from colcon_core.package_augmentation \
    import PackageAugmentationExtensionPoint
from colcon_core.package_augmentation.python \
    import create_dependency_descriptor
from colcon_core.plugin_system import satisfies_version
from colcon_core.subprocess import new_event_loop
from colcon_python_project.hook_caller_decorator \
    import get_decorated_hook_caller
from colcon_python_project.metadata import load_and_cache_metadata
from colcon_python_project.metadata import TEST_EXTRAS
from distlib.util import parse_requirement

logger = colcon_logger.getChild(__name__)


class PEP517PackageAugmentation(PackageAugmentationExtensionPoint):
    """Augment Python packages with `pyproject.toml` using a build backend."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            PackageAugmentationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

        # avoid debug message from asyncio when colcon uses debug log level
        asyncio_logger = logging.getLogger('asyncio')
        asyncio_logger.setLevel(logging.INFO)

    def augment_package(  # noqa: D102
        self, desc, *, additional_argument_names=None
    ):
        if desc.type != 'python.project':
            return

        loop = new_event_loop()
        asyncio.set_event_loop(loop)
        hook_caller = get_decorated_hook_caller(desc)
        # TODO(cottsay): get_requires_for_build_editable
        try:
            deps = loop.run_until_complete(
                    hook_caller.get_requires_for_build_wheel())
        except CalledProcessError as e:
            logger.warn(
                f'An error occurred while reading metadata for {desc.name}:'
                f" {e.stderr.strip().decode() or '(no output)'}")
            asyncio.set_event_loop(None)
            loop.stop()
            loop.close()
            return
        desc.dependencies.setdefault('build', set())
        desc.dependencies['build'].update(
            create_dependency_descriptor(d) for d in deps)

        try:
            metadata = loop.run_until_complete(
                load_and_cache_metadata(desc))
        except CalledProcessError as e:
            logger.warn(
                f'An error occurred while reading metadata for {desc.name}:'
                f" {e.stderr.strip().decode() or '(no output)'}")
            return
        finally:
            asyncio.set_event_loop(None)
            loop.stop()
            loop.close()
        desc.dependencies.setdefault('run', set())
        desc.dependencies.setdefault('test', set())
        for raw_req in metadata.get_all('Requires-Dist', ()):
            req = parse_requirement(raw_req)
            if req.marker:
                if (
                    req.marker['lhs'] == 'extra' and
                    req.marker['op'] == '==' and
                    req.marker['rhs'] in TEST_EXTRAS
                ):
                    desc.dependencies['test'].add(
                        create_dependency_descriptor(raw_req))
            else:
                desc.dependencies['run'].add(
                    create_dependency_descriptor(raw_req))

        if not desc.metadata.get('version'):
            desc.metadata['version'] = metadata['Version']

        maintainers = metadata.get('Maintainer-email')
        if not maintainers:
            maintainers = metadata.get('Author-email')
        if maintainers:
            desc.metadata.setdefault('maintainers', [])
            for maintainer in maintainers.split(','):
                rfc822 = maintainer.strip()
                if rfc822 not in desc.metadata['maintainers']:
                    desc.metadata['maintainers'].append(rfc822)
