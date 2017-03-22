### 1.2.1 [March 22, 2016]
* **BUGFIX** Bugfix in new logging code to avoid warnings when using a logger without a handler [[#15](https://github.com/Instrumental/instrumental_agent-python/pull/15)]

### 1.2.0 [March 22, 2016]
* Make logging configurable and silence it by default [[#14](https://github.com/Instrumental/instrumental_agent-python/pull/14)]

### 1.1.0 [August 8, 2016]
* **BUGFIX**: Preserve timezone information when sending a time with a metric [[#11](https://github.com/Instrumental/instrumental_agent-python/pull/11)]
* make handshake version string match pattern of other 1st-party agents [[#12](https://github.com/Instrumental/instrumental_agent-python/pull/12)]

### 1.0.2 [June 6, 2016]
* Fix time defaulting to agent initialize instead of call time
* Send correct agent version in hello

### 1.0.1 [May 13, 2016]
* Fix reference to old package name in version lookup which would cause the agent to error on initialization
* Use bare socket when testing connection to prevent blocking behavior on an SSL wrapped socket

### 1.0.0 [May 13, 2016]
* No significant code changes

### 0.2.0 [April 13, 2016]
* better connection error handling
* exception handling for all public functions

### 0.1.0 [April 13, 2016]
* BREAKING CHANGE - rename from instrumental to instrumental_agent to avoid naming conflict

### 0.0.1 [April 13, 2016]
* Initial version
