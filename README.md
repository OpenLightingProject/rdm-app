# rdm-app

This is the codebase for the rdm.openlighting.org website.

If you're intested in how PID definitions work, see https://wiki.openlighting.org/index.php/RDM_PID_Definitions

## Development Setup

On the production instance, the javascript is minified using
[UglifyJS](http://lisperator.net/uglifyjs/). Before you start changing the
code, or deploy to appengine you'll need to download the javascript tools that
are used for this process.

The tools are managed using [nodejs](https://github.com/joyent/node)'s package
manager [npm](https://github.com/npm/npm).  The packages are downloaded using
npm and [bower](https://github.com/bower/bower). Bower is called using
[grunt](https://github.com/gruntjs/grunt)

If all of this seems rather complex don't despair, once everything is installed
it's very easy to use.

1, Install npm.

2, Install grunt-cli globally yourself by running either
```bash
npm install -g grunt-cli
```
or
```bash
sudo npm install -g grunt-cli
```

3, Use npm to install the remaining dependencies. In the root directory of the
project run:
```bash
npm install
grunt bower
```

This will install the node.js dependencies (grunt, bower, karma) and then run
the grunt task for installing the bower packages.

### Important!
The bower packages should only be installed using grunt, since grunt will place
them in static/libs, where both appengine & karma expect them. Calling bower
directly will install them in bower_components.

## Common Tasks

Tasks are managed using Grunt. To see a list of tasks run:

```bash
grunt --help
```

### Run the Unit Tests

The newer Angular code is unit-tested using
[karma](https://github.com/karma-runner/karma). The tests are in
unit-test-js/tests/rdm.js and the karma configuration in
unit-test-js/karma.conf.js. The test can be run with:
```bash
grunt unit-test
```
It does require Firefox and the dependencies to be installed to be able to run
the test.

### Compress / Uglify

To minifiy the Javascript code, run
```bash
grunt compress
```

This will run [jshint](http://jshint.com/) which enforces style guidelines and
then if jshint passes, runs uglifyjs to compress the javascript code.

If you are continuously editing the source and testing it,
you can have grunt automatically perform the compression when the source files
change by running
```bash
grunt compress-watch
```

### Debugging

If you are having trouble with debugging the minified sources you can copy
the files to the static dir (without compression) by using:
```bash
grunt copy-once
```

Again, this will run [jshint](http://jshint.com/) and the copy the sources over
to static/js/

If you want an automatic copy when the files change, use:
```bash
grunt copy-watch
```

#### Important!
When you are finished debugging, remember to run
```bash
grunt copy-cleanup
```
otherwise the files won't be compressed

### Deploying to App Engine

Before deploying to App Engine run:
```bash
grunt compress
```

You can then run appcfg.py to deploy.

TODO(someone): Automate this using Grunt.
