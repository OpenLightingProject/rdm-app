module.exports = function(grunt) {
  'use strict';
  require('google-closure-compiler').grunt(grunt);

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
    clean: {
      copy: './static/js/rdm.js'
    },
    copy: {
      develop: {
        src: './js_src/rdm.js',
        dest: './static/js/rdm.js'
      }
    },
    uglify: {
      build: {
        files: [{
          dest: './static/js/rdm.js',
          src: './js_src/rdm.js'//TODO(dave): change this to ./js_scr/*js
        }],
        options: {
          mangle: true,
          sourceMap: true,
          sourceMapName: './static/js/rdm.js.map'
        }
      }
    },
    karma: {
      firefox: {
        configFile: './unit-test-js/karma.conf.js',
        singleRun: true,
        browsers: ['Firefox'],
        reporters: 'dots',
        plugins: [
          'karma-firefox-launcher',
          'karma-jasmine'
        ]
      },
      chrome: {
        configFile: './unit-test-js/karma.conf.js',
        singleRun: true,
        browsers: ['Chrome'],
        reporters: 'dots',
        plugins: [
          'karma-chrome-launcher',
          'karma-jasmine'
        ]
      }
    },
    jshint: {
      dev: [
        'Gruntfile.js',
        'js_src/rdm.js',//TODO(dave): change this to ./js_scr/*js
        'unit-test-js/karma.conf.js',
        'unit-test-js/tests/*js'
      ],
      options: {
        jshintrc: true
      }
    },
    jscs: {
      src: [
        'Gruntfile.js',
        'js_src/rdm.js',//TODO(dave): change this to ./js_scr/*js
        'unit-test-js/karma.conf.js',
        'unit-test-js/tests/*js'
      ],
      options: {
        verbose: true,
        config: true
      }
    },
    watch: {
      build: {
        files: ['Gruntfile.js', 'js_src/rdm.js'],
        tasks: ['jshint:dev', 'uglify:build'],
        options: {
          atBegin: true
        }
      },
      copy: {
        files: ['Gruntfile.js', 'js_src/rdm.js'],
        tasks: ['jshint:dev', 'clean:copy', 'copy:develop'],
        options: {
          atBegin: true
        }
      }
    },
    'closure-compiler': {
      build: {
        options: {
          args: [
            '--js', 'js_src/**.js',
            '--js', '!js_src/rdm.js',
            '--js', 'node_modules/google-closure-library/closure/**.js',
            '--js', 'node_modules/google-closure-library/third_party/**.js',
            '--js', '"!**_test.js"',
            '--jscomp_warning', 'lintChecks',
            '--entry_point', 'app.setup',
            '--js_output_file', 'static/js/app.js',
            '--dependency_mode', 'STRICT',
            '--compilation_level', 'ADVANCED_OPTIMIZATIONS'
          ]
        }
      }
    }
  });
  grunt.loadNpmTasks('grunt-karma');
  grunt.loadNpmTasks('grunt-bower-task');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-jscs');
  grunt.registerTask('default', ['bower']);
  grunt.registerTask('lint', ['jshint:dev', 'jscs']);
  grunt.registerTask('unit-test', ['bower', 'compress', 'karma:firefox']);
  grunt.registerTask('compress', ['lint', 'uglify:build']);
  grunt.registerTask('compress-watch', ['watch:build']);
  grunt.registerTask('copy-once', ['lint', 'clean:copy', 'copy:develop']);
  grunt.registerTask('copy-watch', ['watch:copy']);
  grunt.registerTask('copy-cleanup', ['clean:copy', 'compress']);
};
