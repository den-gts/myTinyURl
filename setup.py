from setuptools import setup, find_packages
from os.path import join, dirname
import tinyurld

setup(
    name='tinyurld',
    version=tinyurld.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    entry_points={
        'console_scripts':
            ['run_server = tinyurld.app:run_server']
    },
    install_requires=[
        'tornado==4.4.1',
        'motor==0.6.2'
    ]
)
