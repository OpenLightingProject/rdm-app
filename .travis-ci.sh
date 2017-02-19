#!/bin/bash
if [[ $TASK = 'nosetests' ]]; then
    nosetests -v 3 --detailed-errors
elif [[ $TASK = 'karma' ]]; then
    export DISPLAY=:99.0
    sh -e /etc/init.d/xvfb start
    grunt unit-test
elif [[ $TASK = 'js-lint' ]]; then
    grunt lint
fi
