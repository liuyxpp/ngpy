try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ngpy',
    version='0.1',
    license='BSD',
    description='Web application for Monte Carlo simulation on nucleation and growth phenomena',
    author='Yi-Xin Liu',
    author_email='liuyxpp@gmail.com',
    url='https://bitbucket.org/liuyxpp/ngpy',
    packages=['ngpy'],
    scripts=['run-ngpy','simd'],
    include_package_data=True,
    zip_safe=False,
    long_description=__doc__,
    platform='linux',
    install_requires=[
        'Flask-WTF>=0.5.2',
        'Flask-ZODB>=0.1',
        'Flask>=0.8',
        'numpy>=1.6.0',
        'matplotlib>=1.0.1',
        'redis>=2.4.9',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Application Frameworks'
    ]
     )

