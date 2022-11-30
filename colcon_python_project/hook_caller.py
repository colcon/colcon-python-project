# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from contextlib import AbstractContextManager
from functools import partialmethod
import os
import pickle
import sys

from colcon_core.subprocess import run
from colcon_python_project.spec import load_and_cache_spec


class _SubprocessTransport(AbstractContextManager):

    def __enter__(self):
        self.child_in, self.parent_out = os.pipe()
        os.set_inheritable(self.child_in, True)
        self.parent_in, self.child_out = os.pipe()
        os.set_inheritable(self.child_out, True)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.close(self.parent_out)
        os.close(self.parent_in)
        os.close(self.child_out)
        os.close(self.child_in)


class AsyncHookCaller:
    """Calls PEP 517 style hooks asynchronously in a new process."""

    def __init__(
        self, backend_name, *, project_path=None, env=None,
        stdout_callback=None, stderr_callback=None,
    ):
        """
        Initialize a new AsyncHookCaller.

        :param backend_name: The name of the PEP 517 build backend.
        :param project_path: Path to the project's root directory.
        :param env: Environment variables to use when invoking hooks.
        :param stdout_callback: Callback for stdout from the hook invocation.
        :param stderr_callback: Callback for stderr from the hook invocation.
        """
        self._backend_name = backend_name
        self._project_path = str(project_path) if project_path else None
        self._env = dict(env) if env else None
        self._stdout_callback = stdout_callback
        self._stderr_callback = stderr_callback

    @property
    def backend_name(self):
        """Get the name of the backend to call hooks on."""
        return self._backend_name

    async def call_hook(self, hook_name, **kwargs):
        """
        Call the given hook with given arguments.

        :param hook_name: Name of the hook to call.
        """
        with _SubprocessTransport() as transport:
            args = [
                sys.executable, '-m', 'colcon_python_project._call_hook',
                self._backend_name, hook_name,
                str(transport.child_in), str(transport.child_out)]
            with os.fdopen(os.dup(transport.parent_out), 'wb') as f:
                pickle.dump(kwargs, f)
            have_callbacks = self._stdout_callback or self._stderr_callback
            process = await run(
                args, self._stdout_callback, self._stderr_callback,
                cwd=self._project_path, env=self._env, close_fds=False,
                capture_output=not have_callbacks)
            process.check_returncode()
            with os.fdopen(os.dup(transport.parent_in), 'rb') as f:
                res = pickle.load(f)
            return res

    # PEP 517
    build_wheel = partialmethod(call_hook, 'build_wheel')
    build_sdist = partialmethod(call_hook, 'build_sdist')
    get_requires_for_build_wheel = partialmethod(
        call_hook, 'get_requires_for_build_wheel')
    prepare_metadata_for_build_wheel = partialmethod(
        call_hook, 'prepare_metadata_for_build_wheel')
    get_requires_for_build_sdist = partialmethod(
        call_hook, 'get_requires_for_build_sdist')

    # PEP 660
    build_editable = partialmethod(call_hook, 'build_editable')
    get_requires_for_build_editable = partialmethod(
        call_hook, 'get_requires_for_build_editable')
    prepare_metadata_for_build_editable = partialmethod(
        call_hook, 'prepare_metadata_for_build_editable')


def get_hook_caller(desc, **kwargs):
    """
    Create a new AsyncHookCaller instance for a package descriptor.

    :param desc: The package descriptor
    """
    spec = load_and_cache_spec(desc)
    return AsyncHookCaller(
        spec['build-system']['build-backend'],
        project_path=desc.path, **kwargs)
