module.exports = function (grunt) {
    'use strict';
    grunt.initConfig({
        bower: {
            libs: {
                options: {
                    targetDir: 'static/libs',
                    install: true,
                    copy: true,
                    cleanup: true,
                    layout: 'byComponent'
                }
            }
        },
        uglify: {
            build: {
                files: [{
                    dest: './static/js/rdm.js',
                    src: './js_src/rdm.js'
                }],
                options: {
                    mangle: true,
                    sourceMap: true,
                    sourceMapName: './static/js/rdm.js.map'
                }
            }
        },
        karma: {
            travis: {
                configFile: './unit-test-js/karma.conf.js',
                singleRun: true,
                browsers: ['Firefox'],
                reporters: 'dots',
                plugins: [
                    'karma-firefox-launcher',
                    'karma-jasmine'
                ]
            }
        }
    });
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-bower-task');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.registerTask('default', ['bower']);
    grunt.registerTask('travis-unit', ['bower', 'karma:travis']);
    grunt.registerTask('compress', ['uglify']);
};
