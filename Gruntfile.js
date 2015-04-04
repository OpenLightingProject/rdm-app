module.exports = function (grunt) {
    'use strict';
    grunt.initConfig({
        bower: {
            libs: {
                options: {
                    targetDir: 'libs',
                    install: true,
                    copy: true,
                    cleanup: true,
                    layout: 'byComponent'
                }
            }
        }
    });
    grunt.loadNpmTasks('grunt-bower-task');
    grunt.registerTask('default', ['bower'])
};
