from setuptools import setup, find_packages

SRC_DIR = 'src'


def get_version():
    import sys

    sys.path[:0] = [SRC_DIR]
    return __import__('easy_alert').__version__


setup(
    name='easy-alert',
    version=get_version(),
    description='Super Simple Process Monitoring Tool',
    author='mogproject',
    author_email='mogproj@gmail.com',
    url='https://github.com/mogproject/easy-alert',
    install_requires=[
        'pyyaml',
        'paramiko',
    ],
    tests_require=[
        'unittest2',
    ],
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    test_suite='tests',
    entry_points="""
    [console_scripts]
    easy-alert = easy_alert.easy_alert:main
    """,
)
