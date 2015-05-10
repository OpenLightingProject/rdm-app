describe('rdmApp', function () {
    beforeEach(browser.get('/index.html'));

    var $controller;

    beforeEach(inject(function (_$controller_) {
        $controller = _$controller_;
    }));

    describe('convertToEUID', function () {
        it('displays error when invalid uid', function () {
            var convertor = {};
            var controller = $controller('UIDController', {$scope: convertor});
            convertor.uid = 'invalidteststring';
            convertor.convertToEUID();
            expect(convertor.error).toEqual('Invalid UID');
            expect(convertor.euid).toEqual('');
        });

        it('displays euid if uid is valid', function () {
            var convertor = {};
            var controller = $controller('UIDController', {$scope: convertor});
            convertor.uid = '7a70:00000001';
            convertor.convertToEUID();
            expect(convertor.error).toEqual('');
            expect(convertor.euid).toEqual('fa 7f fa 75 aa 55 aa 55 aa 55 ab 55 ae 57 ef f5');
        });
    });
    describe('convertToUID', function() {
       it('displays error when invalid euid', function () {
           var convertor = {};
           var controller = $controller('EUIDController', {$scope: convertor});
           convertor.euid = 'invalidteststring';
           convertor.convertToUID();
           expect(convertor.error).toEqual('invalid EUID, only found 1 bytes');
           expect(convertor.uid).toEqual('');
       })
    });
});