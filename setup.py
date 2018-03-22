from setuptools import setup, find_packages


setup(
    name='xparser',
    author='Antonio Todorov',
    email='taeskow@gmail.com',
    license='MIT',
    version='0.0.1',
    packages=find_packages(exclude='tests'),
    include_package_data=True,
    tests_require=['pytest', 'pytest-runner']
)