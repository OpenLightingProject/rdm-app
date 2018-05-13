/* jscs:disable disallowDanglingUnderscores */
describe('rdmApp', function() {
  'use strict';
  var $controller;

  beforeEach(function() {
    module('rdmApp');
  });

  beforeEach(inject(function(_$controller_) {
    $controller = _$controller_;
  }));

  describe('convertToEUID', function() {
    it('displays error when invalid uid', function() {
      var converter = {};
      $controller('UIDController', {$scope: converter});
      converter.uid = 'invalidteststring';
      converter.convertToEUID();
      expect(converter.error).toEqual(
        'Invalid UID, please enter a UID in the form MMMM:NNNNNNNN');
      expect(converter.euid).toEqual('');
    });

    it('displays EUID if UID is valid', function() {
      var converter = {};
      $controller('UIDController', {$scope: converter});
      converter.uid = '7a70:00000001';
      converter.convertToEUID();
      expect(converter.error).toEqual('');
      expect(converter.euid)
        .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');

      converter.uid = '7a7000000001';
      converter.convertToEUID();
      expect(converter.error).toEqual('');
      expect(converter.euid)
        .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');

      converter.uid = '7a 70 00 00 00 01';
      converter.convertToEUID();
      expect(converter.error).toEqual('');
      expect(converter.euid)
        .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');

      converter.uid = '7a.70.00.00.00.01';
      converter.convertToEUID();
      expect(converter.error).toEqual('');
      expect(converter.euid)
        .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');

      converter.uid = '7a-70-00-00-00-01';
      converter.convertToEUID();
      expect(converter.error).toEqual('');
      expect(converter.euid)
        .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');
    });
  });
  describe('convertToUID', function() {
    it('displays error when invalid euid', function() {
      var converter = {};
      $controller('EUIDController', {$scope: converter});
      converter.euid = 'invalidteststring';
      converter.convertToUID();
      expect(converter.error).toEqual(
        'Invalid EUID: Invalid byte: invalidteststring');
      expect(converter.uid).toEqual('');

      converter.euid = '';
      converter.convertToUID();
      expect(converter.error).toEqual(
        'Invalid EUID: insufficient data, should be 16 bytes');
      expect(converter.uid).toEqual('');
    });

    it('displays uid if euid is valid', function() {
      var converter = {};
      $controller('EUIDController', {$scope: converter});
      converter.euid = 'fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5';
      converter.convertToUID();
      expect(converter.error).toEqual('');
      expect(converter.uid).toEqual('7a70:00000001');

      converter.euid =
        'fa, 7f, fa, 75, aa, 55, aa, 55, aa, 55, ab, 55, ae, 57, ef, f5';
      converter.convertToUID();
      expect(converter.error).toEqual('');
      expect(converter.uid).toEqual('7a70:00000001');

      converter.euid = 'fa,7f,fa,75,aa,55,aa,55,aa,55,ab,55,ae,57,ef,f5';
      converter.convertToUID();
      expect(converter.error).toEqual('');
      expect(converter.uid).toEqual('7a70:00000001');
    });
  });
});
