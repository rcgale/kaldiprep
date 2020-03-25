from distutils.core import setup

setup(
    name='kaldiprep',
    version='0.5.0',
    author='Robert Gale',
    author_email='galer@ohsu.edu',
    packages=['kaldiprep'],
    url='https://repo.cslu.ohsu.edu/galer/kaldiprep',
    install_requires=[
        'sortedcontainers'
    ],
)

