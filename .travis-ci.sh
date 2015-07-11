#!/usr/bin/env bash
if [[ $TASK = 'nosetests' ]]; then
#    pip install json-spec
    nosetests
elif [[ $TASK = 'karma' ]]; then
    export DISPLAY=:99.0
    sh -e /etc/init.d/xvfb start
#    npm install -g grunt-cli
#    npm install
    grunt unit-test
elif [[ $TASK = 'js-lint' ]]; then
#    npm install -g grunt-cli
#    npm install
    grunt lint
fi
