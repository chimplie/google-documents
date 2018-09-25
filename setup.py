from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='google_documents',
    version='0.0.5',
    description='Python package to work with Google Documents',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/chimplie/google-documents',
    author='Vitalii Pavliuk',
    author_email='pavliuk96@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['google_documents.tests', 'google_documents.tests.entities']),
    zip_safe=False,
    install_requires=[
        "google-api-python-client==1.6.6",
        "pandas==0.23.4"
    ]
)
