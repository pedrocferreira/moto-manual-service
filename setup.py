from setuptools import setup, find_packages

setup(
    name="moto-manual-service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'django>=4.0.0',
        'djangorestframework>=3.14.0',
        'gunicorn>=21.2.0',
        'python-dotenv>=1.0.0',
        'rakam-systems>=0.1.0',
        'openai>=1.0.0',
        'pandas>=2.0.0',
        'pymupdf>=1.23.0',
    ],
) 