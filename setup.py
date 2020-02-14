from setuptools import setup, find_packages

with open('LICENSE') as f:
    license = f.read()

setup(
    name='python-eStat',
    version='1.0',
    description='Tool for getting eStat data',
    author='Daiki Kanazawa',
    author_email='dkanazawa@jmdc.co.jp',
    url='https://github.com/jmdc-dkanazawa/python-eStat',
    install_requires=['IPython', 'pandas'],
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
