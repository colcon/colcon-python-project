# Copyright 2022 Open Source Robotics Foundation, Inc.
# Licensed under the Apache License, Version 2.0

from base64 import urlsafe_b64encode
from configparser import ConfigParser
from email import message_from_binary_file
from hashlib import sha256
from io import TextIOWrapper
import os.path
from pathlib import Path
import shutil
import warnings
from zipfile import ZIP_DEFLATED
from zipfile import ZipFile

from colcon_core.python_install_path import get_python_install_path
from distlib.scripts import ScriptMaker


def _get_install_path(key, install_base):
    return get_python_install_path(key, {'base': str(install_base)})


def write_and_record(libdir, path, lines):
    """
    Write file content to disk and compute a fully-qualified RECORD entry.

    :param libdir: The library directory where the package is installed.
    :param path: Path to the file to be written, either absolute or
      relative to the library directory.
    :param lines: Enumerable of lines of text to be written.
    :returns: Three-element tuple constituting the file's RECORD entry.
    """
    path = libdir / path
    raw = (os.linesep.join(lines) + os.linesep).encode()
    digest = urlsafe_b64encode(sha256(raw).digest()).rstrip(b'=').decode()
    path.write_bytes(raw)
    return (
        Path(os.path.relpath(path, libdir)).as_posix(),
        f'sha256={digest}',
        f'{len(raw)}')


def install_wheel(wheel_path, install_base, script_dir_override=None):
    """
    Install a wheel file under the given installation base directory.

    :param wheel_path: Path to the wheel file to be installed.
    :param install_base: Path to the base directory to install under.
    :param script_dir_override: Override the default script install
      directory
    """
    wheel_name = wheel_path.name.split('-')
    if len(wheel_name) not in (5, 6):
        raise RuntimeError('Invalid wheel file name')
    distribution, version = wheel_name[:2]
    dist_info_dir = f'{distribution}-{version}.dist-info/'
    data_dir = f'{distribution}-{version}.data/'
    wheel_file = dist_info_dir + 'WHEEL'
    record_file = dist_info_dir + 'RECORD'
    entry_points_file = dist_info_dir + 'entry_points.txt'

    with ZipFile(
        wheel_path, mode='r', compression=ZIP_DEFLATED, allowZip64=True
    ) as wf:
        with wf.open(wheel_file) as wf_mf:
            wheel_metadata = message_from_binary_file(wf_mf)

        wheel_version = wheel_metadata.get('Wheel-Version', '').split('.')
        if len(wheel_version) < 2 or wheel_version[0] != '1':
            raise RuntimeError('Wheel file is not supported')
        elif wheel_version[1] != '0':
            warnings.warn('Wheel format is newer than supported version')

        if wheel_metadata.get('Root-Is-Purelib') in ('true',):
            libdir = _get_install_path('purelib', install_base)
        else:
            libdir = _get_install_path('platlib', install_base)

        records = []
        with wf.open(record_file) as wf_rec_bin:
            with TextIOWrapper(wf_rec_bin) as wf_rec:
                for line in wf_rec:
                    if ',' in line:
                        records.append(line.strip().split(','))

        for record in records:
            if record[0] == record_file:
                continue
            elif not record[0].startswith(data_dir):
                wf.extract(record[0], libdir)
                continue

            _, key, subpath = record[0].split('/', 2)
            target = Path(_get_install_path(key, install_base))
            target /= subpath
            target.parent.mkdir(parents=True, exist_ok=True)
            with wf.open(record[0]) as fsrc:
                with target.open('wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst)
            record[0] = os.path.relpath(target, start=libdir)

        records.append(write_and_record(
            libdir,
            dist_info_dir + 'INSTALLER',
            ('colcon-python-project',)))

        if entry_points_file in wf.namelist():
            ep = ConfigParser()
            with wf.open(entry_points_file) as wf_ep_bin:
                with TextIOWrapper(wf_ep_bin) as wf_ep:
                    ep.read_file(wf_ep)
            if ep.has_section('console_scripts'):
                if script_dir_override:
                    script_dir = install_base / script_dir_override
                else:
                    script_dir = _get_install_path('scripts', install_base)
                sm = ScriptMaker(None, script_dir)
                sm.clobber = True
                sm.variants = {''}
                specs = [
                    '%s = %s' % pair
                    for pair in ep.items('console_scripts')
                ]
                scripts_made = sm.make_multiple(specs)

                records += [
                    (Path(os.path.relpath(s, libdir)).as_posix(), '', '')
                    for s in scripts_made
                ]

        with (libdir / record_file).open('w') as f:
            f.writelines(','.join(rec) + '\n' for rec in records)
