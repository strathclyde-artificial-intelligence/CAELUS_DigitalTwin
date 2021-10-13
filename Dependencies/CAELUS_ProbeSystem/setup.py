from setuptools import setup, find_packages

setup(
   name='ProbeSystem',
   version='1.0',
   description='Python library for telemetry aggregation (CAELUS)',
   author='Leonardo Cascianelli',
   author_email='me.leonardocascianelli@gmail.com',
   packages=find_packages(),
   install_requires=['wheel'],
)