#Instrumental Python Native Client Library

It is compatible with Python 2 and Python 3.


## Installation

```bash
pip install --upgrade instrumental
```

or

```bash
easy_install --upgrade instrumental
```

If you are on a system with `easy_install` but not [`pip`](http://www.pip-installer.org/en/latest/index.html), you can use `easy_install` instead. If you're not using [`virtualenv`](http://www.virtualenv.org/), you may have to prefix those commands with `sudo`.


## Usage

## More Help


## Development


## Release Process

1. Pull latest master
2. Merge feature branch(es) into master
3. `script/test`
4. Increment version
5. Update [CHANGELOG.md](CHANGELOG.md)
6. Commit "Release version vX.Y.Z"
7. Push to GitHub
8. Tag version: `git tag 'vX.Y.Z' && git push --tags`
9. Build packages `python setup.py sdist bdist_wheel`
10. Upload packages `twine upload dist/*`
11. Update documentation on instrumentalapp.com


## Version Policy

This library follows [Semantic Versioning 2.0.0](http://semver.org).
