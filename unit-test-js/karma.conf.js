module.exports = function (config) {
    config.set({

        basePath: '../',

        files: [
            'static/libs/angular/js/angular.min.js',
            'static/libs/angular-mocks/js/angular-mocks.js',
            'static/js/rdm.js',
            'unit-test-js/tests/rdm.js'
        ],

        autoWatch: true,

        frameworks: ['jasmine'],

        browsers: [
            'Chrome',
            'Firefox'
        ],

        plugins: [
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-jasmine'
        ]

    });
};