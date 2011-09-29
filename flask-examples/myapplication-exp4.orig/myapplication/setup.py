# -*- coding:utf-8 -*-

"""
    setup.py
    ~~~~~~~~
    
"""

from setuptools import setup

setup(
    name="myapplication",
    version="0.3",
    url="",
    license="",
    author="Italo Maia",
    author_email="",
    description="Simple growing big example.",
    long_description=__doc__,
    packages=["myapplication"],
    zip_save=False,
    platforms="any",
    install_requires=["Flask", "Flask-SQLAlchemy", "wtforms"],
    include_package_data=True,
    classifiers=[]
)
