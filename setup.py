from setuptools import setup, find_packages
import os

# Read version from __init__.py
def get_version():
    init_file = os.path.join(os.path.dirname(__file__), 'aldryn_accounts', '__init__.py')
    with open(init_file, 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip("'\"")
    return '0.4.0'

setup(
    name='aldryn-accounts',
    version=get_version(),
    url='http://github.com/aldryn/aldryn-accounts',
    license='BSD',
    platforms=['OS Independent'],
    description='A registration and authentication app for Aldryn and the django CMS Cloud.',
    author='Divio AG',
    author_email='developers@divio.ch',
    packages=find_packages(),
    install_requires=(
        'Django>=1.6,<5.0',
        'django-annoying',
        'django-absolute',
        'django-appconf',
        'django-classy-tags',
        'django-class-based-auth-views>0.3',
        'django-emailit',
        'django-sekizai',
        'social-auth-app-django',
        'django-standard-form',
        'django-timezone-field',
        'aldryn-common',
        'dj.chain',
        'pygeoip',
        'six',
    ),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    license_files=['LICENSE'],
)
