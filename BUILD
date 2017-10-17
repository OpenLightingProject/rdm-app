#!/bin/sh

java \
-jar node_modules/google-closure-compiler/compiler.jar \
--js 'js_src/**.js' \
--js 'node_modules/google-closure-library/closure/**.js' \
--js 'node_modules/google-closure-library/third_party/**.js' \
--js '!**_test.js' \
--entry_point 'app.setup' \
--js_output_file static/js/app.js \
--dependency_mode STRICT \
--compilation_level ADVANCED_OPTIMIZATIONS
