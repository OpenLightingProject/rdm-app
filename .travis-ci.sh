#!/usr/bin/env bash
if [[ $TASK = 'nosetests' ]]; then
    nosetests
elif [[ $TASK = 'karma' ]]; then
    export DISPLAY=:99.0
    sh -e /etc/init.d/xvfb start
    npm start
fi