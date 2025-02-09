from setuptools import setup, find_packages

setup(
    name='pylgx',  # Name of your package
    version='1.2.0',  # Starting version
    author='Kyroneff',  # Your name or organization
    author_email='Kyronfroom57@gmail.com',  # Your email
    description='A lightweight logging library for Python with features like log rotation and configurable error levels.',
    long_description=open('README.md').read(),  # Ensure you have a README.md
    long_description_content_type='text/markdown',  # Type of the README file
    url='https://github.com/KyronEff/Logging',  # Your project's URL
    packages=find_packages(),  # Automatically find and include all submodules
    classifiers=[  # Classifiers help others find your package
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version
    install_requires=[  # List your dependencies here, if any
        # 'some_package>=1.0.0',
    ],
    include_package_data=True,  # Include any files listed in MANIFEST.in
    entry_points={  # If your package includes command-line tools
        'console_scripts': [
            'logger-cli=logger.cli:main',  # Example CLI command
        ],
    },
)
