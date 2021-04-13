from setuptools import setup, find_packages

setup(
    name='uldaq_stream',
    version='0.1',
    description = 'a library for streaming data from a MMC USB daq',
    author='Will Dickson',
    author_email='wbd@caltech',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(exclude=['examples',]),
)
