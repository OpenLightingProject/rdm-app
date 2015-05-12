#!/usr/bin/env bash
if [[ $TASK = 'nosetests' ]]; then
    pip install json-spec
    nosetests
elif [[ $TASK = 'karma-firefox' ]]; then
    export DISPLAY=:99.0
    sh -e /etc/init.d/xvfb start
    npm run firefox
elif [[ $TASK = 'karma-phantomjs' ]]; then
    npm run phantomjs
fi