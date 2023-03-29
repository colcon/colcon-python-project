# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from configparser import ConfigParser
import logging
import os.path
from pathlib import Path
from subprocess import CalledProcessError

from colcon_core.environment import create_environment_hooks
from colcon_core.environment import create_environment_scripts
from colcon_core.event.output import StderrLine
from colcon_core.event.output import StdoutLine
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import get_command_environment
from colcon_core.task import TaskExtensionPoint
from colcon_python_project.hook_caller_decorator \
    import get_decorated_hook_caller
from colcon_python_project.wheel import install_wheel

logger = colcon_logger.getChild(__name__)


class PythonProjectBuildTask(TaskExtensionPoint):
    """Build Python project packages."""

    def __init__(self):  # noqa: D107
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

        # avoid debug message from asyncio when colcon uses debug log level
        asyncio_logger = logging.getLogger('asyncio')
        asyncio_logger.setLevel(logging.INFO)

        distutils_logger = logging.getLogger('distlib.util')
        distutils_logger.setLevel(logging.WARN)

    async def build(self, *, additional_hooks=None):  # noqa: D102
        pkg = self.context.pkg
        args = self.context.args

        logger.info(f"Building Python project in '{args.path}'")

        script_dir_override = None
        setup_cfg_path = pkg.path / 'setup.cfg'
        if setup_cfg_path.is_file():
            parser = ConfigParser()
            with setup_cfg_path.open() as f:
                parser.read_file(f)
            if args.symlink_install:
                script_dir_override = parser.get(
                    'develop', 'script-dir', fallback=None)
                if not script_dir_override:
                    script_dir_override = parser.get(
                        'develop', 'script_dir', fallback=None)
            else:
                script_dir_override = parser.get(
                    'install', 'install-scripts', fallback=None)
                if not script_dir_override:
                    script_dir_override = parser.get(
                        'install', 'install_scripts', fallback=None)

            # Resolve setuptools-specific syntax
            if script_dir_override:
                _override = Path(args.install_base)
                for part in Path(script_dir_override).parts:
                    if part == '$base':
                        part = args.install_base
                    _override /= part
                script_dir_override = _override

        env = await get_command_environment(
            'python_project', args.build_base, self.context.dependencies)

        hook_caller = get_decorated_hook_caller(
            pkg, env=env, stdout_callback=self._stdout_callback,
            stderr_callback=self._stderr_callback)

        wheel_directory = Path(args.build_base) / 'wheel'
        wheel_directory.mkdir(parents=True, exist_ok=True)
        try:
            build_hook_name = 'build_wheel'
            if args.symlink_install:
                hook_names = await hook_caller.list_hooks()
                if 'build_editable' in hook_names:
                    build_hook_name = 'build_editable'
                else:
                    logger.info(
                        f"Backend '{hook_caller.backend_name}' does not "
                        'support --symlink-install - falling back to regular '
                        "build for package '{pkg.name}'")
            wheel_name = await hook_caller.call_hook(
                build_hook_name, wheel_directory=wheel_directory)
        except CalledProcessError as e:
            return e.returncode

        wheel_path = wheel_directory / wheel_name
        dist_info_dir = install_wheel(
            wheel_path, args.install_base,
            script_dir_override=script_dir_override)

        libdir = dist_info_dir.parent
        records = []

        hooks = create_environment_hooks(args.install_base, pkg.name)
        records += [
            (Path(os.path.relpath(hook, libdir)).as_posix(), '', '')
            for hook in hooks
        ]

        scripts = create_environment_scripts(
            pkg, args, default_hooks=hooks, additional_hooks=additional_hooks)
        records += [
            (Path(os.path.relpath(script, libdir)).as_posix(), '', '')
            for script in scripts
        ]

        if build_hook_name == 'build_editable':
            # PEP 610
            direct_url_json = dist_info_dir / 'direct_url.json'
            with direct_url_json.open('w') as f:
                f.write(
                    f'{{"url":"{pkg.path.absolute().as_uri()}",'
                    '"dir_info":{"editable":true}}\n')
            records.append((
                Path(os.path.relpath(direct_url_json, libdir)).as_posix(),
                '', ''))

        with (dist_info_dir / 'RECORD').open('a') as f:
            f.writelines(','.join(rec) + '\n' for rec in records)

    def _stdout_callback(self, line):
        self.context.put_event_into_queue(StdoutLine(line))

    def _stderr_callback(self, line):
        self.context.put_event_into_queue(StderrLine(line))
