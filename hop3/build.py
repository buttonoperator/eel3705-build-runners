# -*- coding: utf-8 -*-
"""Regenerate every diagram and reassemble index.html.

    python build.py

Runs the three SVG generators, then inlines their output into src/template.html
and writes the single-file page to index.html at the repository root.
"""
import os
import subprocess
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
STAGES = [
    ('gen.py', 'breadboard placement diagram'),
    ('gen2.py', 'signal flow schematic'),
    ('gen3.py', 'IC pin map'),
    ('build.py', 'page assembly and checks'),
]


def main():
    for script, what in STAGES:
        print('==> %-10s %s' % (script, what))
        r = subprocess.run([sys.executable, '-I', script], cwd=SRC)
        if r.returncode:
            return r.returncode
    print('\nindex.html written.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
