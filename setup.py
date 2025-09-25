# setup.py
from pathlib import Path
from setuptools import setup, find_packages
import re

ROOT = Path(__file__).parent

def read_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")

def get_version() -> str:
    """
    Read __version__ from aldryn_accounts/__init__.py without importing the package.
    """
    init = read_text("aldryn_accounts/__init__.py")
    m = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", init, re.M)
    return m.group(1) if m else "0.4.0"

setup(
    name="aldryn-accounts",
    version=get_version(),
    url="https://github.com/aldryn/aldryn-accounts",
    license="BSD-3-Clause",
    description="A registration and authentication app for Aldryn and the django CMS Cloud.",
    long_description=read_text("README.md") if (ROOT / "README.md").exists() else "",
    long_description_content_type="text/markdown",
    author="Divio AG",
    author_email="developers@divio.ch",
    packages=find_packages(exclude=("tests", "tests.*")),
    include_package_data=True,   # include package data specified by MANIFEST.in
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "Django>=1.11,<5.0",
        "django-annoying",
        "django-absolute",
        "django-appconf",
        "django-classy-tags",
        "django-class-based-auth-views>0.3",
        "django-emailit",
        "django-sekizai",
        "social-auth-app-django",
        "django-standard-form",
        "django-timezone-field",
        "aldryn-common",
        "dj.chain",
        "pygeoip",
        "six",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
    ],
    project_urls={
        "Source": "https://github.com/aldryn/aldryn-accounts",
        "Tracker": "https://github.com/aldryn/aldryn-accounts/issues",
    },
    license_files=["LICENSE"],  # ensures license is included in sdists/wheels
)
