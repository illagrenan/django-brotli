# -*- encoding: utf-8 -*-
# ! python3

import shutil
import warnings

from invoke import task

PROJECT_NAME = 'django_brotli'


@task
def clean(ctx):
    """remove build artifacts"""
    shutil.rmtree('{PROJECT_NAME}.egg-info'.format(PROJECT_NAME=PROJECT_NAME), ignore_errors=True)
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('dist', ignore_errors=True)
    shutil.rmtree('htmlcov', ignore_errors=True)
    shutil.rmtree('__pycache__', ignore_errors=True)


@task
def test(ctx):
    ctx.run("pytest tests/")


@task
def coverage(ctx):
    """check code coverage quickly with the default Python"""
    ctx.run("coverage run --source {PROJECT_NAME} -m pytest".format(PROJECT_NAME=PROJECT_NAME))
    ctx.run("coverage report -m")
    ctx.run("coverage html")


@task
def check(ctx):
    """Check setup"""
    ctx.run("python setup.py --no-user-cfg --verbose check --metadata --restructuredtext --strict")


@task
def test_install(ctx):
    """try to install built package"""
    ctx.run("pip uninstall {PROJECT_NAME} --yes".format(PROJECT_NAME=PROJECT_NAME), warn=True)
    ctx.run("pip install --no-cache-dir --no-index --find-links=file:./dist {PROJECT_NAME}".format(PROJECT_NAME=PROJECT_NAME))
    ctx.run("pip uninstall {PROJECT_NAME} --yes".format(PROJECT_NAME=PROJECT_NAME))


@task
def build(ctx):
    """build package"""
    ctx.run("python setup.py build")
    ctx.run("python setup.py sdist")
    ctx.run("python setup.py bdist_wheel")


@task
def publish(ctx):
    """publish package"""
    warnings.warn("Deprecated", DeprecationWarning, stacklevel=2)

    check(ctx)
    ctx.run('python setup.py sdist upload -r pypi')  # Use python setup.py REGISTER
    ctx.run('python setup.py bdist_wheel upload -r pypi')


@task
def publish_twine(ctx):
    """publish package"""
    check(ctx)
    ctx.run('twine upload dist/* --skip-existing')


@task
def publish_test(ctx):
    """publish package"""
    check(ctx)
    ctx.run('python setup.py sdist upload -r https://test.pypi.org/legacy/')  # Use python setup.py REGISTER
    ctx.run('python setup.py bdist_wheel upload -r https://test.pypi.org/legacy/')
