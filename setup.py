import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='Ezyt',
    version=read(VERSION),
    author='Alexander Bacho',
    author_email='alex.sani.bacho@gmail.com',
    description=('Helps with fully and semi-automating the creation of youtube videos.'),
    license='MIT',
    keywords='ezyt youtube reddit 4chan vimeo automation',
    url='https://github.com/AlexBacho/ezyt',
    packages=setuptools.find_packages(),
    long_description=read('README'),
    classifiers=[
        'Development Status :: pre-Alpha',
        "Programming Language :: Python :: 3",
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
)