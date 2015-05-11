module.exports = function (config) {
    config.set({

        basePath: '../',

        files: [
            'libs/angular/js/angular.min.js',
            'libs/angular-mocks/js/angular-mocks.js',
            'js/rdm.js',
            'unit-test-js/e2e-tests/scenarios.js'
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