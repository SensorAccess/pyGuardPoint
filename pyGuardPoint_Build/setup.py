from setuptools import setup, find_packages

# README.rst is written in Markdown-compatible style (setext headings, indented code) and
# renders correctly on PyPI as Markdown - it is NOT valid reStructuredText, so keep the
# content type as text/markdown.
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(name="pyGuardPoint",
      # pysignalr>=1.3.0 requires Python >=3.10, so 3.9 cannot install this package.
      python_requires='>=3.10',
      # tests/ ships in the sdist (see MANIFEST.in) but is not installed: as a top-level
      # 'tests' package it would shadow other projects' tests, and its imports
      # (pyGuardPoint_Build.pyGuardPoint) only resolve from a source checkout.
      packages=find_packages(exclude=['tests', 'tests.*']),
      data_files=[
          ('', ['CLAUDE.md', 'llms.txt']),
      ],
      version="3.0.0",
      author="John Owen",
      description="Python wrapper for GuardPoint 10 Access Control System",
      long_description_content_type='text/markdown',
      long_description=long_description,
      maintainer_email="sales@sensoraccess.co.uk",
      # aiohttp is imported directly by GuardPointAsyncIO - declare it rather than relying
      # on pysignalr pulling it in.
      install_requires=['validators', 'fuzzywuzzy', 'cryptography', 'pysignalr>=1.3.0', 'websockets',
                        'python-Levenshtein', 'aiohttp'],
      license="Apache-2.0",
      license_files=('LICENSE.txt',),
      zip_safe=False)
