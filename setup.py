from setuptools import setup, find_packages
from os.path import join, dirname, basename
import tinyurld

setup(
    name='tinyurld',
    version=tinyurld.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    data_files=[
                    (dirname(tinyurld.default_config),
                     ['conf/settings.py.example', ]
                     ),
                ],
    entry_points={
        'console_scripts':
            ['tinyurld = tinyurld.app:run_server']
    },
    install_requires=[
        'tornado==4.4.1',
        'motor==0.6.2', 'mock'
    ]
)
