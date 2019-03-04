#!/usr/bin/env python
from __future__ import print_function
'Setuptools installation file'
__url__ = 'http://github.com/silnrsi/pysilfont'
__copyright__ = 'Copyright (c) 2014 SIL International (http://www.sil.org)'
__license__ = 'Released under the MIT License (http://opensource.org/licenses/MIT)'
__version__ = '1.4.2.dev0'

import sys, os, imp

try:
    from setuptools import setup
except ImportError :
    print("pysilfont requires setuptools - see installation notes in README.md")
    sys.exit(1)

warnings = []
if sys.argv[1] in ('develop', 'install') :
    for m in ('fontforge', 'fontTools', 'ufo2ft', 'defcon', 'ufoLib', 'cu2qu', 'robofab', 'glyphsLib', 'compreffor', 'booleanOperations', 'fontMath', 'mutatorMath', 'odf', 'fontParts'):
        try:
            imp.find_module(m)
        except ImportError : warnings.append("- Some modules/scripts require the python %s package which is not currently installed" % m)

long_description =  "A growing collection of font utilities mainly written in Python designed to help with various aspects of font design and production.\n"
long_description += "Developed and maintained by SIL International's Non-Roman Script Initiative (NRSI).\n"
long_description += "Some of these utilites make use of the FontForge Python module."


# Create entry_points console scripts entry
cscripts = []
for file in os.listdir("lib/silfont/scripts/") :
    (base,ext) = os.path.splitext(file)
    if ext == ".py" and base != "__init__" : cscripts.append(base + " = silfont.scripts." + base + ":cmd")

setup(
    name = 'pysilfont',
    version = __version__,
    description = 'Python-based font utilities collection',
    long_description = long_description,
    maintainer = 'NRSI - SIL International',
    maintainer_email = 'fonts@sil.org',
    url = 'http://github.com/silnrsi/pysilfont',
    packages = ["silfont", "silfont.scripts"],
    package_dir = {'':'lib'},
    entry_points={'console_scripts': cscripts},
    license = 'MIT',
    platforms = ['Linux','Win32','Mac OS X'],
    classifiers = [
        "Environment :: Console",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Fonts"
        ],
)

if warnings :
    print ("\n***** Warnings *****")
    for warning in warnings : print(warning)

