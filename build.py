# -*- coding: utf-8 -*-
"""Rebuild every project page, or the ones named.

    python build.py            # all projects
    python build.py hop3       # just one

Each project folder has its own build.py, which regenerates that project's diagrams and
writes its index.html. This script runs them in turn and stops on the first failure.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECTS = ['hop2', 'hop3']


def main(argv):
    names = argv or PROJECTS
    for name in names:
        if name not in PROJECTS:
            print('unknown project %r; choose from %s' % (name, ', '.join(PROJECTS)))
            return 2
        print('\n######## %s' % name)
        r = subprocess.run([sys.executable, '-I', 'build.py'], cwd=os.path.join(ROOT, name))
        if r.returncode:
            return r.returncode
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
