#!/bin/bash
if [[ $TASK = 'nosetests' ]]; then
    nosetests --verbosity=3 --detailed-errors
elif [[ $TASK = 'karma' ]]; then
    export DISPLAY=:99.0
    sh -e /etc/init.d/xvfb start
    grunt unit-test
elif [[ $TASK = 'js-lint' ]]; then
    grunt lint
elif [[ $TASK = 'data-check' ]]; then
    ./tools/make_manufacturer_data.sh > data/manufacturer_data.py && git diff --exit-code data/manufacturer_data.py
fi
