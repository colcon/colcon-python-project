# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from tempfile import TemporaryDirectory

from colcon_core.plugin_system import satisfies_version
from colcon_python_project.hook_caller_decorator import GenericDecorator
from colcon_python_project.hook_caller_decorator \
    import HookCallerDecoratorExtensionPoint
from packaging.version import Version

try:
    from setuptools import __version__ as setuptools_version
except ImportError:
    setuptools_version = '0'


if Version(setuptools_version) < Version('64'):
    ESCAPE_HATCH = '--global-option'
else:
    ESCAPE_HATCH = '--build-option'


class SetuptoolsHookCallerDecoratorExtension(
    HookCallerDecoratorExtensionPoint
):
    """Decorate a hook caller for a setuptools-based backend."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(
            HookCallerDecoratorExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def decorate_hook_caller(self, *, hook_caller):  # noqa: D102
        if hook_caller.backend_name not in (
            'setuptools.build_meta',
            'setuptools.build_meta:__legacy__',
        ):
            return hook_caller
        return SetuptoolsDecorator(hook_caller)


class _ScratchBuildBase(TemporaryDirectory):

    def __init__(self, config_settings):
        self._config_settings = config_settings
        super().__init__()

    def __enter__(self):
        temp = super().__enter__()
        self._config_settings.setdefault(ESCAPE_HATCH, [])
        self._config_settings[ESCAPE_HATCH] += [
            'build',
            f'--build-base={temp}',
        ]
        return temp

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)


class _ScratchEggBase(TemporaryDirectory):

    def __init__(self, config_settings):
        self._config_settings = config_settings
        super().__init__()

    def __enter__(self):
        temp = super().__enter__()
        self._config_settings.setdefault(ESCAPE_HATCH, [])
        self._config_settings[ESCAPE_HATCH] += [
            'egg_info',
            f'--egg-base={temp}',
        ]
        return temp

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)


class SetuptoolsDecorator(GenericDecorator):
    """Enhance hooks to the setuptools build backend."""

    async def call_hook(self, hook_name, **kwargs):  # noqa: D102
        if hook_name not in (
            'build_wheel',
            'get_requires_for_build_wheel',
            'prepare_metadata_for_build_wheel',
        ):
            return await self._decoree.call_hook(hook_name, **kwargs)

        config_settings = kwargs.pop('config_settings', {})
        with _ScratchEggBase(config_settings):
            with _ScratchBuildBase(config_settings):
                return await self._decoree.call_hook(
                    hook_name, config_settings=config_settings, **kwargs)
