from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='lenses_python',
    version='2.3',
    packages=['lenses_python'],
    url='https://github.com/Landoop/lenses-python',
    download_url='https://github.com/Landoop/lenses-python/archive/2.3.tar.gz',
    license='Apache License 2.0',
    author='Filippas Serepas',
    author_email='info@lenses.io',
    description='Lenses Python Client',
    long_descripion=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3',
    install_requires=['requests', 'pandas==0.23.3', 'websocket-client==0.47.0', 'sseclient-py==1.7', 'kerberos']
)
