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
   var convertor = {};
   $controller('UIDController', {$scope: convertor});
   convertor.uid = 'invalidteststring';
   convertor.convertToEUID();
   expect(convertor.error).toEqual(
     'Invalid UID, please enter a UID in the form MMMM:NNNNNNNN');
   expect(convertor.euid).toEqual('');
  });

  it('displays EUID if UID is valid', function() {
   var convertor = {};
   $controller('UIDController', {$scope: convertor});
   convertor.uid = '7a70:00000001';
   convertor.convertToEUID();
   expect(convertor.error).toEqual('');
   expect(convertor.euid)
    .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');

   convertor.uid = '7a7000000001';
   convertor.convertToEUID();
   expect(convertor.error).toEqual('');
   expect(convertor.euid)
    .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');

   convertor.uid = '7a 70 00 00 00 01';
   convertor.convertToEUID();
   expect(convertor.error).toEqual('');
   expect(convertor.euid)
    .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');

   convertor.uid = '7a.70.00.00.00.01';
   convertor.convertToEUID();
   expect(convertor.error).toEqual('');
   expect(convertor.euid)
    .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');

   convertor.uid = '7a-70-00-00-00-01';
   convertor.convertToEUID();
   expect(convertor.error).toEqual('');
   expect(convertor.euid)
    .toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');
  });
 });
 describe('convertToUID', function() {
  it('displays error when invalid euid', function() {
   var convertor = {};
   $controller('EUIDController', {$scope: convertor});
   convertor.euid = 'invalidteststring';
   convertor.convertToUID();
   expect(convertor.error).toEqual('Invalid EUID: Non hex characters');
   expect(convertor.uid).toEqual('');

   convertor.euid = '';
   convertor.convertToUID();
   expect(convertor.error).toEqual(
     'Invalid EUID: insufficent data, should be 32 hex characters');
   expect(convertor.uid).toEqual('');
  });

  it('displays uid if euid is valid', function() {
   var convertor = {};
   $controller('EUIDController', {$scope: convertor});
   convertor.euid = 'fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5';
   convertor.convertToUID();
   expect(convertor.error).toEqual('');
   expect(convertor.uid).toEqual('7a70:00000001');

   convertor.euid =
    'fa, 7f, fa, 75, aa, 55, aa, 55, aa, 55, ab, 55, ae, 57, ef, f5';
   convertor.convertToUID();
   expect(convertor.error).toEqual('');
   expect(convertor.uid).toEqual('7a70:00000001');

   convertor.euid = 'fa,7f,fa,75,aa,55,aa,55,aa,55,ab,55,ae,57,ef,f5';
   convertor.convertToUID();
   expect(convertor.error).toEqual('');
   expect(convertor.uid).toEqual('7a70:00000001');
  });
 });
});
