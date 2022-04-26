from setuptools import setup, find_packages

with open('README.md', 'r') as file_handle:
    long_description = file_handle.read()

setup(
    name='atomdateparser',
    version='0.0.1',
    author='Daniel Lovegrove',
    author_email='d.lovegrove11@gmail.com',
    description='Parse eventDates for AtoM CSVs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/NationalCentreTruthReconciliation/AtoM-Event-Date-Parser',
    license='MIT',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    scripts=[],
    install_requires=[
        "dateparser>=1.0.0",
    ],
    python_requires='>=3.6',
)
