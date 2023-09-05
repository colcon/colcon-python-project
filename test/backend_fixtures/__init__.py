# Copyright 2023 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from .flit import mock_backend_project as mock_flit_project  # noqa: F401
from .legacy import mock_backend_project as mock_legacy_project  # noqa: F401
from .poetry import mock_backend_project as mock_poetry_project  # noqa: F401
from .setuptools \
    import mock_backend_project as mock_setuptools_project  # noqa: F401


MOCK_BACKENDS = ('flit', 'legacy', 'poetry', 'setuptools')
