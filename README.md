#Instrumental Python Agent

Instrumental is a [application monitoring platform](https://instrumentalapp.com) built for developers who want a better understanding of their production software. Powerful tools, like the [Instrumental Query Language](https://instrumentalapp.com/docs/query-language), combined with an exploration-focused interface allow you to get real answers to complex questions, in real-time.

This agent supports custom metric monitoring for Python applications, compatible with Python 2 and Python 3. It provides high-data reliability at high scale, without ever blocking your process or causing an exception.


## Installation

```bash
pip install --upgrade instrumental_agent
```

or

```bash
easy_install --upgrade instrumental_agent
```

If you are on a system with `easy_install` but not [`pip`](http://www.pip-installer.org/en/latest/index.html), you can use `easy_install` instead. If you're not using [`virtualenv`](http://www.virtualenv.org/), you may have to prefix those commands with `sudo`.


## Usage

Visit [instrumentalapp.com](https://instrumentalapp.com) and create an account, then initialize the agent with your API token, found in the [token documentation](https://instrumentalapp.com/docs/tokens).

```python
from instrumental_agent import Agent
i = Agent("PROJECT_API_TOKEN", enabled=True)
```

You'll  probably want something like the above, only enabling the agent in production mode so you don't have development and production data writing to the same place. Or you can setup two projects, so that you can verify stats in one, and release them to production in another.

Now you can begin to use Instrumental to track your application.

```python
i.gauge('load', 1.23)                         # value at a point in time

i.increment('signups')                        # increasing value, think "events"

i.time('query_time', lambda: Post.find(1))    # time a method call

i.time_ms('query_time', lambda: Post.find(1)) # prefer milliseconds?
```

**Note**: For your app's safety, the agent is meant to isolate your app from any problems our service might suffer. If it is unable to connect to the service, it will discard data after reaching a low memory threshold.

Want to track an event (like an application deploy, or downtime)? You can capture events that are instantaneous, or events that happen over a period of time.

```sh
i.notice('Jeffy deployed rev ef3d6a') # instantaneous event
i.notice('Testing socket buffer increase', time.time(), timedelta(minutes=20)) # an event with a duration
```


## Server Metrics

Want server stats like load, memory, etc.? Check out [InstrumentalD](https://github.com/instrumental/instrumentald).

## Release Process

1. Pull latest master
2. Merge feature branch(es) into master
3. `script/test`
4. Increment version in:
  - `setup.py`
  - `instrumental_agent/agent.py`
5. Update [CHANGELOG.md](CHANGELOG.md)
6. Commit "Release vX.Y.Z"
7. Push to GitHub
8. Tag version: `git tag 'vX.Y.Z' && git push --tags`
9. Build packages `python setup.py sdist bdist_wheel`
10. Upload packages `twine upload dist/*`
11. Update documentation on instrumentalapp.com


## Version Policy

This library follows [Semantic Versioning 2.0.0](http://semver.org).
