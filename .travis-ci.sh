#!/bin/bash


PYCHECKER_BLACKLIST=""
#threading,unittest,cmd,optparse,google,google.protobuf,ssl,fftpack,lapack_lite,mtrand

if [[ $TASK = 'nosetests' ]]; then
    nosetests --verbosity=3 --detailed-errors
elif [[ $TASK = 'karma' ]]; then
    export DISPLAY=:99.0
    sh -e /etc/init.d/xvfb start
    grunt --verbose unit-test
elif [[ $TASK = 'js-lint' ]]; then
    grunt --verbose lint
elif [[ $TASK = 'closure-compiler' ]]; then
    grunt --verbose closure-compiler
elif [[ $TASK = 'data-check' ]]; then
    ./tools/make_manufacturer_data.sh > data/manufacturer_data.py && git diff --exit-code data/manufacturer_data.py
elif [[ $TASK = 'spellintian' ]]; then
  # run the spellchecker only if it is the requested task
  spellingfiles=$(find ./ -type f -and ! \( \
      -wholename "./.git/*" -or \
      -wholename "./node_modules/*" \
      \) | xargs)
  # count the number of spellchecker errors
  spellingerrors=$(zrun spellintian $spellingfiles 2>&1 | \
      grep -v "./README.md: Tasks Tasks (duplicate word)" | \
      grep -v "./model.py: label label (duplicate word)" | \
      wc -l)
  if [[ $spellingerrors -ne 0 ]]; then
    # print the output for info
    zrun spellintian $spellingfiles \
        grep -v "./README.md: Tasks Tasks (duplicate word)" | \
        grep -v "./model.py: label label (duplicate word)"
    echo "Found $spellingerrors spelling errors"
    exit 1;
  else
    echo "Found $spellingerrors spelling errors"
  fi;
elif [[ $TASK = 'codespell' ]]; then
  # run codespell only if it is the requested task
  spellingfiles=$(find ./ -type f -and ! \( \
      -wholename "./.git/*" -or \
      -wholename "./node_modules/*" \
      \) | xargs)
  # count the number of codespell errors
  spellingerrors=$(zrun codespell --check-filenames --quiet 2 --regex "[a-zA-Z0-9][\\-'a-zA-Z0-9]+[a-zA-Z0-9]" --exclude-file .codespellignore $spellingfiles 2>&1 | wc -l)
  if [[ $spellingerrors -ne 0 ]]; then
    # print the output for info
    zrun codespell --check-filenames --quiet 2 --regex "[a-zA-Z0-9][\\-'a-zA-Z0-9]+[a-zA-Z0-9]" --exclude-file .codespellignore $spellingfiles
    echo "Found $spellingerrors spelling errors via codespell"
    exit 1;
  else
    echo "Found $spellingerrors spelling errors via codespell"
  fi;
elif [[ $TASK = 'flake8' ]]; then
  flake8 --max-line-length 80 --exclude .git,__pycache,node_modules/* --ignore E111,E114,E129 $(find ./ -name "*.py" | xargs)
  #,E121,E127
elif [[ $TASK = 'pychecker' ]]; then
  PYTHONPATH=./:$PYTHONPATH
  export PYTHONPATH
  pychecker --quiet --limit 500 --blacklist $PYCHECKER_BLACKLIST $(find ./ -name "*.py" | xargs)
elif [[ $TASK = 'pychecker-wip' ]]; then
  PYTHONPATH=./:$PYTHONPATH
  export PYTHONPATH
  pychecker --quiet --limit 500 --blacklist $PYCHECKER_BLACKLIST $(find ./ -name "*.py" | xargs)
fi
