from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(name="pyGuardPoint",
      packages=find_packages(),
      version="1.7.0",
      author="John Owen",
      description="Python wrapper for GuardPoint 10 Access Control System",
      long_description_content_type='text/markdown',
      long_description=long_description,
      maintainer_email="sales@sensoraccess.co.uk",
      install_requires=['validators', 'fuzzywuzzy', 'cryptography', 'pysignalr', 'websockets', 'python-Levenshtein'],
      #packages=['pyGuardPoint'],
      license_files=('LICENSE.txt',),
      zip_safe=False)
