# filepath: my_package/setup.py
from setuptools import setup, find_packages

setup(
    name='generative-ai-for-beginners',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'openai',
        'azure-identity',
        'python-dotenv',
        # Add other dependencies here
    ],
    author='Jayman Dalal',
    author_email='jdalal@microsoft.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)