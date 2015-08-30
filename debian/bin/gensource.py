#!/usr/bin/env python3

import sys
sys.path.append("debian/lib/python")

import io
import os
import os.path
import subprocess
import tarfile
import tempfile
import time

from debian_linux.debian import Changelog, VersionLinux


class Main(object):
    def __init__(self):
        self.log = sys.stdout.write

        changelog = Changelog(version=VersionLinux)[0]
        source = changelog.source
        version = changelog.version

        self.tar_orig = '{}_{}.orig.tar.xz'.format(source, version.upstream)
        self.tar_debian = '{}_{}-{}.debian.tar.xz'.format(source, version.upstream, version.revision)

        self.revs = {
                'orig': self.source_revision('orig'),
                'none': self.source_revision('none'),
        }

        from pprint import pprint
        pprint(self.__dict__)

    def __call__(self):
        self.create_tar()

        subprocess.check_call((
            'dpkg-source',
            '--target-format=3.0 (quilt)',
            '--build', '.',
            self.tar_orig,
            self.tar_debian,
        ))

    def source_revision(self, name):
        return subprocess.check_output((
            'git',
            '--git-dir=source/{}/.git'.format(name),
            'rev-parse', 'HEAD',
        )).decode('ascii').strip()

    def create_tar(self):
        with tarfile.open('../{}'.format(self.tar_debian), mode='w:xz', debug=2) as tar:
            tar.add("debian", filter=self.tar_debian_filter)

            with io.BytesIO(b'3.0 (quilt)\n') as f:
                t = tarfile.TarInfo('debian/source/format')
                t.size = len(f.getvalue())
                tar.addfile(t, f)

            t = tarfile.TarInfo('debian/patches')
            t.mode = 0o755
            t.type = tarfile.DIRTYPE
            tar.addfile(t)

            self.create_tar_patch(tar, 'none')

    def create_tar_patch(self, tar, name):
        if name == 'none':
            patch = 'patch'
            series = 'series'
            revs = (self.revs['orig'], self.revs['none'])
        else:
            raise NotImplementedError
            patch = 'patch-{}'.format(name)
            series = 'series-{}'.format(name)
            revs = (self.revs['none'], self.revs[name])

        patch_file = 'debian/patches/{}'.format(patch)
        series_file = 'debian/patches/{}'.format(series)

        with io.BytesIO('{}\n'.format(patch).encode('ascii')) as f:
            t = tarfile.TarInfo(series_file)
            t.size = len(f.getvalue())
            tar.addfile(t, f)

        with tempfile.TemporaryFile() as f:
            subprocess.check_call((
                'git',
                '--git-dir=source/{}/.git'.format(name),
                'diff', '{}..{}'.format(*revs)
            ), stdout=f)

            t = tarfile.TarInfo(patch_file)
            t.size = f.tell()
            f.seek(0)
            tar.addfile(t, f)

    @staticmethod
    def tar_debian_filter(tarinfo):
        if tarinfo.name in ('debian/build', 'debian/source/format', 'debian/stamps'):
            return
        if tarinfo.name.endswith('.local'):
            return

        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = ""
        return tarinfo

if __name__ == '__main__':
    Main()()
