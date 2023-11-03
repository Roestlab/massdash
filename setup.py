import sys
from setuptools import setup, find_packages

# read the contents of README for PyPI
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='MassSeer',
      version="0.1.0-alpha.0",
      author="Justin Sing",
      author_email="justincsing@gmail.com",
      description="MassSeer: Streamlined DIA-MS visualization, analysis,  optimization and rapid prototyping.",
      long_description=long_description,
      long_description_content_type='text/markdown',
      license="BSD",
      url="https://github.com/Roestlab/massseer",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Scientific/Engineering :: Chemistry',
      ],
      zip_safe=False,
      install_requires=[
          "Click",
          "streamlit",
          "numpy >= 1.9.0",
          "pandas >= 0.17",
          "cython==0.29.32",
          "scipy",
          "pyopenms",
          "PyMSNumpress==0.2.2",
          "bokeh==2.4.3",
          "matplotlib"
      ],
      entry_points={
          'console_scripts': [
              "MassSeer=massseer.main:cli",
              ]
      }
      )
