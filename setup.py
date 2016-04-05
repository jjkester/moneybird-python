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
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='moneybird api client oauth consumer',
)
