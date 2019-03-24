from setuptools import find_packages, setup

setup(
    name='simplewc',
    version='0.0.1-dev',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests',
        'beautifulsoup4',
        'redis',
        'grpcio',
        'grpcio_tools',
        'pymongo'
        # 'pytest' # Only for testing.

    ],
)
