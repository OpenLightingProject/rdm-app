module.exports = function(config){
  config.set({

    basePath : './',

    files : [
      'libs/angular/js/angular.min.js',
      'libs/angular-mocks/js/angular-mocks.js',
      'js/rdm.js',
      'e2e-tests/scenarios.js'
    ],

    autoWatch : true,

    frameworks: ['jasmine'],

    browsers : ['Chrome'],

    plugins : [
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-jasmine',
            'karma-junit-reporter'
            ]

  });
};