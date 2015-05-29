# rdm-app

This is the codebase for the rdm.openlighting.org website.

If you're intested in how PID definitions work, see https://wiki.openlighting.org/index.php/RDM_PID_Definitions

## Get dependencies

Before you upload to appengine or start developing you'll have to download some javascript dependencies.
These can be downloaded using [nodejs](https://github.com/joyent/node)'s package manager [npm](https://github.com/npm/npm).
The packages get downloaded using [bower](https://github.com/bower/bower) and [grunt](https://github.com/gruntjs/grunt)
You have to install grunt-cli globally yourself by running either
```bash
npm install -g grunt-cli
```
or
```bash
sudo npm install -g grunt-cli
```
and to install all the other dependencies of the project, run in the root directory of the project
```bash
npm install
grunt bower
```
Which first installs the node.js dependencies (grunt, bower, karma) and then runs the grunt task for installing the bower packages

### Important! 
only install bower packages through grunt, because grunt moves them to static/libs and appengine and karma both expect
them to be there and not in bower_components also static/libs has a different structure then bower_components.

## Run unit-tests for rdm.js

Currently only rdm.js in static/js has a javascript unit-test using [karma](https://github.com/karma-runner/karma) the unit-test is
located in unit-test-js/tests/rdm.js and the karma configuration in unit-test-js/karma.conf.js the test can be run by running
```bash
grunt unit-test
```
It does require firefox and the dependencies to be installed to be able to run the test

## Compress rdm.js

The source for static/js/rdm.js is in js_src/rdm.js. however when you adjust rdm.js you have to compress it
you can do this by running 
```bash
grunt compress
```
or if you are continuously adjusting the source and testing it,
and you just want to automate the compressing of rdm.js run
```bash
grunt compress-watch
```

## Debug rdm.js

if you are having troubles with debugging the minified source of rdm.js you can copy
the files to the static dir using
```bash
grunt copy-once
```
or if you want a automatic copy run
```bash
grunt copy-watch
```
### Important!
when you are done debugging don't forget to run
```bash
grunt copy-cleanup
```
otherwise the files won't be compressed