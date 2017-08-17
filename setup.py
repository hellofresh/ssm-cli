from setuptools import setup

setup(
    name='ssm-cli',
    version='0.1',
    py_modules=['ssm'],
    include_package_data=True,
    install_requires=[
        'click',
        'boto3',
        'tabulate'
    ],
    entry_points='''
        [console_scripts]
        ssm=ssm:cli
    '''
)
