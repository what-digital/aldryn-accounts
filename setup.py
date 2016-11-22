from setuptools import setup, find_packages

setup(
    name='aldryn-accounts',
    version=__import__('aldryn_accounts').__version__,
    url='http://github.com/aldryn/aldryn-accounts',
    license='BSD',
    platforms=['OS Independent'],
    description='A registration and authentication app for Aldryn and the django CMS Cloud.',
    author='Divio AG',
    author_email='developers@divio.ch',
    packages=find_packages(),
    install_requires=(
        'Django>=1.6,<1.10',
        'django-annoying',
        'django-absolute',
        'django-appconf',
        'django-classy-tags',
        'django-class-based-auth-views>0.3',
        'django-emailit',
        # 'django-gravatar2',
        'django-password-reset',
        'django-sekizai',
        'python-social-auth',
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
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
