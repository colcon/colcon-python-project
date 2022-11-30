# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from tempfile import TemporaryDirectory

from colcon_core.plugin_system import satisfies_version
from colcon_python_project.hook_caller_decorator import GenericDecorator
from colcon_python_project.hook_caller_decorator \
    import HookCallerDecoratorExtensionPoint


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
        self._config_settings.setdefault('--build-option', [])
        self._config_settings['--build-option'] += [
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
        self._config_settings.setdefault('--build-option', [])
        self._config_settings['--build-option'] += [
            'egg_info',
            f'--egg-base={temp}',
        ]
        return temp

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)


class SetuptoolsDecorator(GenericDecorator):
    """Enhance hooks to the setuptools build backend."""

    async def build_wheel(self, **kwargs):  # noqa: D102
        config_settings = kwargs.pop('config_settings', {})
        with (
            _ScratchEggBase(config_settings),
            _ScratchBuildBase(config_settings),
        ):
            return await self._decoree.build_wheel(
                config_settings=config_settings, **kwargs)

    async def get_requires_for_build_wheel(self, **kwargs):  # noqa: D102
        config_settings = kwargs.pop('config_settings', {})
        with _ScratchEggBase(config_settings):
            return await self._decoree.get_requires_for_build_wheel(
                config_settings=config_settings, **kwargs)

    async def prepare_metadata_for_build_wheel(self, **kwargs):  # noqa: D102
        config_settings = kwargs.pop('config_settings', {})
        with _ScratchEggBase(config_settings):
            return await self._decoree.prepare_metadata_for_build_wheel(
                config_settings=config_settings, **kwargs)
