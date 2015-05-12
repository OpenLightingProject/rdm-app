# rdm-app

This is the codebase for the rdm.openlighting.org website.

If you're intested in how PID definitions work, see https://wiki.openlighting.org/index.php/RDM_PID_Definitions

## Get dependencies

Before you upload to appengine or start developing you'll probably want to download some javascript dependencies.
These can be downloaded using [nodejs](https://github.com/joyent/node)'s package manager [npm](https://github.com/npm/npm).
The packages get downloaded using [bower](https://github.com/bower/bower) and [grunt](https://github.com/gruntjs/grunt) but 
these get installed through npm by running
```bash
npm run dependencies
```
Which first installs the node.js dependencies (grunt, bower, karma) and then runs the grunt task for installing the bower packages

### Important! 
only install bower packages through grunt, because grunt moves them to static/libs and appengine and karma both expect
them to be there and not in bower_components also static/libs has a different structure then bower_components.

## Run unit-tests for rdm.js

Currently only rdm.js in static/js has a javascript unit-test using [karma](https://github.com/karma-runner/karma) the unit-test is
located in unit-test-js/e2e-test/scenarios.js and the karma configuration in unit-test-js/karma.conf.js the test can be run by running
```bash
npm start
```
It does require firefox to be installed to be able to run the test