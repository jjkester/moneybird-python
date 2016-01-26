from distutils.core import setup

from moneybird.api import VERSION

setup(
    name='moneybird',
    version=VERSION,
    packages=['moneybird'],
    url='https://github.com/jjkester/moneybird-python',
    license='MIT',
    author='Jan-Jelle Kester',
    author_email='janjelle@jjkester.nl',
    description='MoneyBird API and OAuth client library',
    install_requires=['requests'],
)
