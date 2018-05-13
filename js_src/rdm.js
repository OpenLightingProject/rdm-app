angular.module('rdmApp', [])
  .config(['$interpolateProvider', function($interpolateProvider) {
    'use strict';
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
  }])

  .constant('RDM', {
    'COMMAND_CLASS': {
      'DISCOVERY_COMMAND': 0x10,
      'DISCOVERY_COMMAND_RESPONSE': 0x11,
      'GET_COMMAND': 0x20,
      'GET_COMMAND_RESPONSE': 0x21,
      'SET_COMMAND': 0x30,
      'SET_COMMAND_RESPONSE': 0x31
    },
    'EUID_SIZE': 16,
    'NACK_REASON': {
      'NR_UNKNOWN_PID': 0x0,
      'NR_FORMAT_ERROR': 0x1,
      'NR_HARDWARE_FAULT': 0x2,
      'NR_PROXY_REJECT': 0x3,
      'NR_WRITE_PROTECT': 0x4,
      'NR_UNSUPPORTED_COMMAND_CLASS': 0x5,
      'NR_DATA_OUT_OF_RANGE': 0x6,
      'NR_BUFFER_FULL': 0x7,
      'NR_PACKET_SIZE_UNSUPPORTED': 0x8,
      'NR_SUB_DEVICE_OUT_OF_RANGE': 0x9,
      'NR_PROXY_BUFFER_FULL': 0x10,
      'NR_ACTION_NOT_SUPPORTED': 0x11
    },
    'PIDS': {
      'DISC_UNIQUE_BRANCH': 0x0001,
      'DISC_MUTE': 0x0002,
      'DISC_UN_MUTE': 0x0003,
      'PROXIED_DEVICES': 0x0010,
      'PROXIED_DEVICE_COUNT': 0x0011,
      'COMMS_STATUS': 0x0015,
      'QUEUED_MESSAGE': 0x0020,
      'STATUS_MESSAGES': 0x0030,
      'STATUS_ID_DESCRIPTION': 0x0031,
      'CLEAR_STATUS_ID': 0x0032,
      'SUB_DEVICE_STATUS_REPORT_THRESHOLD': 0x0033,
      'SUPPORTED_PARAMETERS': 0x0050,
      'PARAMETER_DESCRIPTION': 0x0051,
      'DEVICE_INFO': 0x0060,
      'PRODUCT_DETAIL_ID_LIST': 0x0070,
      'DEVICE_MODEL_DESCRIPTION': 0x0080,
      'MANUFACTURER_LABEL': 0x0081,
      'DEVICE_LABEL': 0x0082,
      'FACTORY_DEFAULTS': 0x0090,
      'LANGUAGE_CAPABILITIES': 0x00a0,
      'LANGUAGE': 0x00b0,
      'SOFTWARE_VERSION_LABEL': 0x00c0,
      'BOOT_SOFTWARE_VERSION_ID': 0x00c1,
      'BOOT_SOFTWARE_VERSION_LABEL': 0x00c2,
      'DMX_PERSONALITY': 0x00E0,
      'DMX_PERSONALITY_DESCRIPTION': 0x00e1,
      'DMX_START_ADDRESS': 0x00f0,
      'SLOT_INFO': 0x0120,
      'SLOT_DESCRIPTION': 0x0121,
      'DEFAULT_SLOT_VALUE': 0x0122,
      'SENSOR_DEFINITION': 0x0200,
      'SENSOR_VALUE': 0x0201,
      'RECORD_SENSORS': 0x0202,
      'DEVICE_HOURS': 0x0400,
      'LAMP_HOURS': 0x0401,
      'LAMP_STRIKES': 0x0402,
      'LAMP_STATE': 0x0403,
      'LAMP_ON_MODE': 0x0404,
      'DEVICE_POWER_CYCLES': 0x0405,
      'DISPLAY_INVERT': 0x0500,
      'DISPLAY_LEVEL': 0x0501,
      'PAN_INVERT': 0x0600,
      'TILT_INVERT': 0x0601,
      'PAN_TILT_SWAP': 0x0602,
      'REAL_TIME_CLOCK': 0x0603,
      'IDENTIFY_DEVICE': 0x1000,
      'RESET_DEVICE': 0x1001,
      'POWER_STATE': 0x1010,
      'PERFORM_SELFTEST': 0x1020,
      'SELF_TEST_DESCRIPTION': 0x1021,
      'CAPTURE_PRESET': 0x1030,
      'PRESET_PLAYBACK': 0x1031,
      'DMX_BLOCK_ADDRESS': 0x0140,
      'DMX_FAIL_MODE': 0x0141,
      'DMX_STARTUP_MODE': 0x0142,
      'DIMMER_INFO': 0x0340,
      'MINIMUM_LEVEL': 0x0341,
      'MAXIMUM_LEVEL': 0x0342,
      'CURVE': 0x0343,
      'CURVE_DESCRIPTION': 0x0344,
      'OUTPUT_RESPONSE_TIME': 0x0345,
      'OUTPUT_RESPONSE_TIME_DESCRIPTION': 0x0346,
      'MODULATION_FREQUENCY': 0x0347,
      'MODULATION_FREQUENCY_DESCRIPTION': 0x0348,
      'BURN_IN': 0x0440,
      'LOCK_PIN': 0x0640,
      'LOCK_STATE': 0x0641,
      'LOCK_STATE_DESCRIPTION': 0x0642,
      'IDENTIFY_MODE': 0x1040,
      'PRESET_INFO': 0x1041,
      'PRESET_STATUS': 0x1042,
      'PRESET_MERGEMODE': 0x1043,
      'POWER_ON_SELF_TEST': 0x1044,
      'LIST_INTERFACES': 0x0700,
      'INTERFACE_LABEL': 0x0701,
      'INTERFACE_HARDWARE_ADDRESS_TYPE1': 0x0702,
      'IPV4_DHCP_MODE': 0x0703,
      'IPV4_ZEROCONF_MODE': 0x0704,
      'IPV4_CURRENT_ADDRESS': 0x0705,
      'IPV4_STATIC_ADDRESS': 0x0706,
      'INTERFACE_RENEW_DHCP': 0x0707,
      'INTERFACE_RELEASE_DHCP': 0x0708,
      'INTERFACE_APPLY_CONFIGURATION': 0x0709,
      'IPV4_DEFAULT_ROUTE': 0x070a,
      'DNS_NAME_SERVER': 0x070b,
      'DNS_HOSTNAME': 0x070c,
      'DNS_DOMAIN_NAME': 0x070d
    },
    'RESPONSE_TYPE': {
      'ACK': 0,
      'ACK_TIMER': 1,
      'NACK': 2,
      'ACK_OVERFLOW': 3
    },
    'START_CODE': 0xcc,
    'SUB_DEVICE': {
      'ROOT_DEVICE': 0x0000,
      'ALL_SUB_DEVICES': 0xffff
    },
    'SUB_DEVICE_MIN': 0x0001,
    'SUB_DEVICE_MAX': 0x0200,
    'SUB_START_CODE': 0x01,
    'UID_SIZE': 6
  })

  .constant('OUTPUT_FORMAT', {
    'C_ARRAY': {'label': 'C Array', 'value': 0},
    'C_STRING': {'label': 'C String', 'value': 1},
    'RAW_HEX': {'label': 'Raw Hex', 'value': 2}
  })

  .service('checksumService', function() {
    'use strict';
    var checksum = function(input) {
      var sum = input.reduce(
        function(previousValue, currentValue, index, array) {
          return previousValue + currentValue;
        }
      );
      return sum;
    };

    this.checksumAsArray = function(input) {
      var sum = checksum(input);
      return [sum >> 8, sum & 0xff];
    };

    this.checksumAsValue = checksum;
  })

  .service('rdmHelperService', ['RDM', function(RDM) {
    'use strict';
    this.isRequest = function(command_class) {
      return command_class === RDM.COMMAND_CLASS.DISCOVERY_COMMAND ||
        command_class === RDM.COMMAND_CLASS.GET_COMMAND ||
        command_class === RDM.COMMAND_CLASS.SET_COMMAND;
    };

    this.isResponse = function(command_class) {
      return command_class === RDM.COMMAND_CLASS.DISCOVERY_COMMAND_RESPONSE ||
        command_class === RDM.COMMAND_CLASS.GET_COMMAND_RESPONSE ||
        command_class === RDM.COMMAND_CLASS.SET_COMMAND_RESPONSE;
    };

    this.isGetSet = function(command_class) {
      return command_class === RDM.COMMAND_CLASS.GET_COMMAND ||
        command_class === RDM.COMMAND_CLASS.GET_COMMAND_RESPONSE ||
        command_class === RDM.COMMAND_CLASS.SET_COMMAND ||
        command_class === RDM.COMMAND_CLASS.SET_COMMAND_RESPONSE;
    };
  }])

  .service('formatService', ['RDM', function(RDM) {
    'use strict';
    var pad = function(length) {
      return new Array(length + 1).join(' ');
    };

    var toHex = function(num, places, prefix, suffix) {
      var str = num.toString(16);
      var zero = places - str.length + 1;
      return ((prefix ? prefix : '') +
      new Array(+(zero > 0 && zero)).join('0') +
      str + (suffix ? suffix : ''));
    };
    this.toHex = toHex;

    this.reverseLookup = function(dictionary, needle) {
      var item = '';
      angular.forEach(dictionary, function(value, key) {
        if (value === needle) {
          item = key;
        }
      });
      return item;
    };

    this.arrayToUID = function(data) {
      if (data.length !== RDM.UID_SIZE) {
        return '';
      }
      return toHex(data[0], 2) + toHex(data[1], 2) + ':' +
        toHex(data[2], 2) + toHex(data[3], 2) +
        toHex(data[4], 2) + toHex(data[5], 2);
    };

    this.arrayToHex = function(input, prefix, suffix) {
      return input.map(function(i) {
        return toHex(i, 2, prefix, suffix);
      });
    };

    this.dataAsArray = function(data, wrap) {
      var indent = 2;
      var prefix = 'const uint8_t packet[] = {';
      var lines = [prefix];
      var current_line = pad(2);
      for (var i = 0; i < data.length; ++i) {
        var str = toHex(data[i], 2, '0x');
        if (current_line.length + str.length + 2 >= wrap) {
          current_line += ',';
          lines.push(current_line);
          current_line = pad(indent);
        } else if (current_line.length !== indent) {
          current_line += ', ';
        }
        current_line += str;
      }
      if (current_line) {
        lines.push(current_line);
      }
      lines.push('};');
      return lines.join('\n');
    };

    this.dataAsString = function(data, wrap) {
      var lines = [];
      var prefix = 'const char packet[] = "';
      var current_line = prefix;
      for (var i = 0; i < data.length; ++i) {
        var str = toHex(data[i], 2, '\\x');
        if (current_line.length + str.length + 2 >= wrap) {
          current_line += '"';
          lines.push(current_line);
          current_line = pad(prefix.length - 1) + '"';
        }
        current_line += str;
      }
      if (current_line) {
        current_line += '";';
        lines.push(current_line);
      }
      return lines.join('\n');
    };

    this.dataAsRawHex = function(data, wrap) {
      var lines = [];
      var current_line = '';
      for (var i = 0; i < data.length; ++i) {
        var str = toHex(data[i], 2);
        if (current_line.length + str.length + 1 >= wrap) {
          lines.push(current_line);
          current_line = '';
        }
        current_line += str;
        if (i + 1 !== data.length) {
          current_line += ' ';
        }
      }
      if (current_line) {
        lines.push(current_line);
      }
      return lines.join('\n');
    };
  }])

  .service('parserService', ['$log', 'RDM', function($log, RDM) {
    'use strict';
    var guessDataFormat = function(tokens) {
      /*
       * Try to determine how to interpret digits like '10'. We do this by
       * looking at the other data supplied.
       * This works well for RDM packets, because the start code is either 0xCC
       * or 204 so we only have to check the first token.
       */
      for (var j = 0; j < tokens.length; j++) {
        // If any of the tokens contain hex characters, default to hex.
        var token = tokens[j];
        if (token.match(/^[a-fA-F]{1,2}$/)) {
          return true;
        }

        // If any tokens are 3 digits, default to decimal.
        if (token.match(/^[\d]{3}$/)) {
          return true;
        }

        // If any tokens are in the form ##h or 0x##, assume tokens not in this
        // format are decimal.
        if (token.match(/^[\da-fA-F]{1,2}h$/) ||
          token.match(/^0x[\da-fA-F]{1,2}$/)) {
          return false;
        }
      }
      // default to decimal
      return false;
    };

    var parseLines = function(lines, as_hex) {
      // If as_hex isn't defined we try to be clever about what we accept.
      // ##h and 0x## are obviously hex values, ## is ambiguous so we use
      // heuristics to figure it out.
      var error = '';
      var binary_data = [];

      var tokens = [];
      for (var i = 0; i < lines.length; ++i) {
        var line = lines[i].replace(/^(.*?)\s*\/\/.*$/, '$1');
        line = line.replace(/[,:\-]/g, ' ');
        line = line.replace(/\s{2,}/g, ' ').trim();
        if (line) {
          tokens = tokens.concat(line.split(' '));
        }
      }

      if (as_hex === undefined) {
        as_hex = guessDataFormat(tokens);
      }

      for (var j = 0; j < tokens.length; j++) {
        var token = tokens[j];
        var hex_suffix_match = token.match(/^([\da-fA-F]{1,2})h$/);
        if (hex_suffix_match) {
          binary_data.push(parseInt(hex_suffix_match[0], 16));
          continue;
        }

        var hex_prefix_match = token.match(/^0x([\da-fA-F]{1,2})$/);
        if (hex_prefix_match) {
          binary_data.push(parseInt(hex_prefix_match[0], 16));
          continue;
        }

        if (as_hex) {
          var hex_match = token.match(/^([\da-fA-F]{1,2})$/);
          if (hex_match) {
            binary_data.push(parseInt(hex_match[0], 16));
            continue;
          } else {
            error = 'Invalid byte: ' + token;
            return [error, binary_data];
          }
        } else {
          var decimal_match = token.match(/^(\d{1,3})$/);
          if (decimal_match) {
            if (decimal_match[0] <= 255) {
              binary_data.push(parseInt(decimal_match[0], 10));
              continue;
            } else {
              error = 'Invalid byte: ' + token;
              return [error, binary_data];
            }
          }
        }

        error = 'Invalid binary data: ' + token;
      }
      return [error, binary_data];
    };

    this.textToBytes = function(text, as_hex) {
      var lines = text.split('\n');
      return parseLines(lines, as_hex);
    };

    this.uidToBytes = function(text) {
      var clean_uid = text.replace(/[\.:\-\s]/g, '');
      if (!clean_uid.match(/^[0-9a-fA-F]{12}$/)) {
        return ['Contains non hex characters', []];
      }

      if (clean_uid.length !== RDM.UID_SIZE * 2) {
        return ['UID should be ' + RDM.UID_SIZE + ' bytes', []];
      }

      var uid_bytes = [];
      for (var i = 0; i < clean_uid.length / 2; i++) {
        var octet = clean_uid.slice(i * 2, (i + 1) * 2);
        var value = parseInt(octet, 16);
        if (isNaN(value)) {
          return ['Invalid UID: bad value' + octet, []];
        }
        uid_bytes.push(value);
      }

      return ['', uid_bytes];
    };
  }])

  .filter('byteToHex', ['formatService', function(formatService) {
    'use strict';
    return function(input) {
      return formatService.toHex(input, 2, '0x');
    };
  }])

  .controller('UIDController',
  ['$scope', '$log', 'checksumService', 'formatService',
    'parserService',
    function($scope, $log, checksumService, formatService,
             parserService) {
      'use strict';
      var OUTPUT_FORMATS = {
        'HEX_SUFFIX': {'label': '##h', 'value': 0},
        'HEX_PREFIX': {'label': '0x##', 'value': 1},
        'HEX_PAIRS': {'label': 'Hex Pairs (##)', 'value': 2},
        'DECIMAL_PAIRS': {'label': 'Decimal Pairs (##)', 'value': 3}
      };

      $scope.invalid_input_message = 'Invalid UID, please enter a UID in the ' +
        'form MMMM:NNNNNNNN';
      $scope.uid = '';
      $scope.euid = '';
      $scope.error = '';
      $scope.OUTPUT_FORMATS = OUTPUT_FORMATS;
      $scope.format = OUTPUT_FORMATS.HEX_PAIRS.value;

      $scope.convertToEUID = function() {
        $scope.euid = '';
        $scope.error = '';

        var return_data = parserService.uidToBytes($scope.uid);
        if (return_data[0]) {
          $scope.error = $scope.invalid_input_message;
          return;
        }
        var uid_bytes = return_data[1];

        var euid_bytes = [];
        angular.forEach(uid_bytes, function(value, index) {
          this.push(value | 0xaa);
          this.push(value | 0x55);
        }, euid_bytes);

        var checksum = checksumService.checksumAsArray(euid_bytes);

        angular.forEach(checksum, function(value, index) {
          this.push(value | 0xaa);
          this.push(value | 0x55);
        }, euid_bytes);

        if ($scope.format === OUTPUT_FORMATS.HEX_SUFFIX.value) {
          $scope.euid = formatService.arrayToHex(euid_bytes, '', 'h').join(' ');
        } else if ($scope.format === OUTPUT_FORMATS.HEX_PREFIX.value) {
          $scope.euid = formatService.arrayToHex(euid_bytes, '0x').join(' ');
        } else if ($scope.format === OUTPUT_FORMATS.HEX_PAIRS.value) {
          $scope.euid = formatService.arrayToHex(euid_bytes).join(' ');
        } else {
          $scope.euid = euid_bytes.join(' ');
        }
      };
    }])

  .controller('EUIDController',
  ['$scope', '$log', 'checksumService', 'formatService',
    'parserService', 'RDM',
    function($scope, $log, checksumService, formatService,
             parserService, RDM) {
      'use strict';
      var INPUT_FORMATS = {
        'DECIMAL': {'label': 'Decimal', 'value': 0},
        'HEX': {'label': 'Hexadecimal', 'value': 1}
      };

      $scope.INPUT_FORMATS = INPUT_FORMATS;
      $scope.format = INPUT_FORMATS.HEX.value;

      $scope.euid = '';
      $scope.error = '';
      $scope.uid = '';

      $scope.convertToUID = function() {
        $scope.error = '';
        $scope.uid = '';

        var return_data = parserService.textToBytes(
          $scope.euid, $scope.format === INPUT_FORMATS.HEX.value);

        if (return_data[0]) {
          $scope.error = 'Invalid EUID: ' + return_data[0];
          return;
        }

        var data = return_data[1];

        if (data.length !== RDM.EUID_SIZE) {
          $scope.error = 'Invalid EUID: insufficient data, should be 16 bytes';
          return;
        }

        var uid_array = [
          data[0] & data[1],
          data[2] & data[3],
          data[4] & data[5],
          data[6] & data[7],
          data[8] & data[9],
          data[10] & data[11]
        ];

        var recovered_checksum = ((data[12] & data[13]) << 8) +
          (data[14] & data[15]);

        var calculated_checksum =
          checksumService.checksumAsValue(data.slice(0, 12));
        if (recovered_checksum !== calculated_checksum) {
          $scope.error = 'Checksum mismatch, was ' + recovered_checksum +
            ', calculated to be ' + calculated_checksum;
          return;
        }

        $scope.uid = formatService.arrayToUID(uid_array);
      };
    }])

  .controller('RDMPacketBuilder',
  ['$scope', '$log', 'checksumService', 'parserService',
    'formatService', 'rdmHelperService', 'OUTPUT_FORMAT',
    'RDM',
    function($scope, $log, checksumService, parserService,
             formatService, rdmHelperService, OUTPUT_FORMAT,
             RDM) {
      'use strict';
      $scope.packet = {
        'start_code': RDM.START_CODE,
        'sub_start_code': 1,
        'dest_uid': '7a70:00000000',
        'src_uid': '7a70:12345678',
        'transaction_number': 0,
        'port_id': 0,
        'message_count': 0,
        'sub_device': 0,
        'command_class': RDM.COMMAND_CLASS.DISCOVERY_COMMAND,
        'param_id': 0,
        'response_type': 0,
        'nack_reason': 0,
        'ack_timer': 0,
        'param_data': '',
        'lower_uid': '',
        'upper_uid': ''
      };

      $scope.properties = {
        'is_request': false,
        'show_param_data': false,
        'pids': []
      };

      $scope.settings = {
        'output_format': OUTPUT_FORMAT.C_ARRAY.value,
        'wrap': 80
      };

      $scope.RDM = RDM;
      $scope.command_classes = [];
      angular.forEach(RDM.COMMAND_CLASS, function(value, key) {
        this.push({
          'value': value,
          'label': key + ' (' + formatService.toHex(value, 2, '0x') + ')'
        });
      }, $scope.command_classes);
      $scope.command_classes.sort(function(a, b) {
        return (( a.value === b.value ) ? 0 :
          (( a.value > b.value ) ? 1 : -1 ));
      });

      $scope.OUTPUT_FORMAT = {};
      angular.forEach(OUTPUT_FORMAT, function(value, key) {
        this[value.label] = value.value;
      }, $scope.OUTPUT_FORMAT);

      $scope.output = '';
      $scope.error = '';

      var parseUIDOrSetError = function(uid, uid_name) {
        var parse_return = parserService.uidToBytes(uid);
        if (parse_return[0]) {
          $scope.error = 'Invalid ' + uid_name + ' UID:' + parse_return[0];
          return '';
        }
        return parse_return[1];
      };

      var showHideParamData = function() {
        $scope.properties.show_param_data = (
        rdmHelperService.isGetSet($scope.packet.command_class) &&
        ($scope.packet.response_type === RDM.RESPONSE_TYPE.ACK ||
        $scope.packet.response_type === RDM.RESPONSE_TYPE.ACK_OVERFLOW));
      };

      var commandClassChanged = function(new_value, old_value, scope) {
        $scope.packet.command_class = new_value;
        $scope.properties.is_request = rdmHelperService.isRequest(new_value);
        showHideParamData();
        var discovery_pids = [
          'DISC_UNIQUE_BRANCH',
          'DISC_MUTE',
          'DISC_UN_MUTE'
        ];

        var pid_names = [];
        if (new_value === RDM.COMMAND_CLASS.DISCOVERY_COMMAND) {
          pid_names = discovery_pids;
        } else if (new_value === RDM.COMMAND_CLASS.DISCOVERY_COMMAND_RESPONSE) {
          pid_names = ['DISC_MUTE', 'DISC_UN_MUTE'];
        } else {
          angular.forEach(RDM.PIDS, function(value, key) {
            if (discovery_pids.indexOf(key) === -1) {
              this.push(key);
            }
          }, pid_names);
        }

        var found_selected = false;
        var pids = [];
        angular.forEach(pid_names, function(key, index) {
          found_selected |= $scope.packet.param_id === RDM.PIDS[key];
          var label = key +
            ' (' + formatService.toHex(RDM.PIDS[key], 4, '0x') + ')';
          this.push({'label': label, 'value': RDM.PIDS[key]});
        }, pids);

        pids.sort(function(a, b) {
          return (( a.label === b.label ) ? 0 :
            ( ( a.label > b.label ) ? 1 : -1 ));
        });

        if (!found_selected) {
          $scope.packet.param_id = pids[0].value;
        }
        $scope.properties.pids = pids;
      };

      var responseTypeChanged = function(newValue, oldValue, scope) {
        $scope.packet.response_type = newValue;
        showHideParamData();
      };

      $scope.$watch('packet.response_type', responseTypeChanged);
      $scope.$watch('packet.command_class', commandClassChanged);

      $scope.buildPacket = function() {
        $scope.error = '';

        var dest_uid =
          parseUIDOrSetError($scope.packet.dest_uid, 'destination');
        if (!dest_uid) {
          return;
        }

        var src_uid = parseUIDOrSetError($scope.packet.src_uid, 'source');
        if (!src_uid) {
          return;
        }

        var param_data = [];
        if ($scope.packet.command_class ===
          RDM.COMMAND_CLASS.DISCOVERY_COMMAND &&
          $scope.packet.param_id === RDM.PIDS.DISC_UNIQUE_BRANCH) {
          var lower_uid = parseUIDOrSetError($scope.packet.lower_uid, 'lower');
          if (!lower_uid) {
            return;
          }
          var upper_uid = parseUIDOrSetError($scope.packet.upper_uid, 'upper');
          if (!upper_uid) {
            return;
          }
          param_data = lower_uid.concat(upper_uid);
        } else if (rdmHelperService.isGetSet($scope.packet.command_class)) {
          if ($scope.packet.response_type === RDM.RESPONSE_TYPE.ACK ||
            $scope.packet.response_type === RDM.RESPONSE_TYPE.ACK_OVERFLOW) {
            var parse_return =
              parserService.textToBytes($scope.packet.param_data);
            if (parse_return[0]) {
              $scope.error = 'Invalid parameter data: ' + parse_return[0];
              return;
            }
            param_data = parse_return[1];
          } else if ($scope.packet.response_type ===
            RDM.RESPONSE_TYPE.NACK) {
            param_data = [$scope.packet.nack_reason >> 8,
              $scope.packet.nack_reason & 0xff];
          } else if ($scope.packet.response_type ===
            RDM.RESPONSE_TYPE.ACK_TIMER) {
            param_data = [$scope.packet.ack_timer >> 8,
              $scope.packet.ack_timer & 0xff];
          }
        }

        var data = [
          $scope.packet.start_code,
          $scope.packet.sub_start_code,
          param_data.length + 24
        ];

        data = data.concat(dest_uid);
        data = data.concat(src_uid);
        data.push($scope.packet.transaction_number);
        if (rdmHelperService.isRequest($scope.packet.command_class)) {
          data.push($scope.packet.port_id);
          data.push(0);  // message count
        } else {
          data.push($scope.packet.response_type);
          data.push($scope.packet.message_count);
        }

        data.push($scope.packet.sub_device >> 8);
        data.push($scope.packet.sub_device & 0xff);
        data.push($scope.packet.command_class);
        data.push($scope.packet.param_id >> 8);
        data.push($scope.packet.param_id & 0xff);

        data.push(param_data.length);
        data = data.concat(param_data);
        data = data.concat(checksumService.checksumAsArray(data));

        if ($scope.settings.output_format ===
          OUTPUT_FORMAT.C_ARRAY.value) {
          $scope.output =
            formatService.dataAsArray(data, $scope.settings.wrap);
        } else if ($scope.settings.output_format ===
          OUTPUT_FORMAT.C_STRING.value) {
          $scope.output =
            formatService.dataAsString(data, $scope.settings.wrap);
        } else if ($scope.settings.output_format ===
          OUTPUT_FORMAT.RAW_HEX.value) {
          $scope.output =
            formatService.dataAsRawHex(data, $scope.settings.wrap);
        }
      };
    }])

  .controller('RDMPacketParser',
  ['$scope', '$log', 'checksumService', 'parserService',
    'formatService', 'rdmHelperService', 'RDM',
    function($scope, $log, checksumService, parserService,
             formatService, rdmHelperService, RDM) {
      'use strict';
      $scope.packet_data = '';
      $scope.show_output = false;

      $scope.RDM = RDM;

      var resetPacket = function() {
        $scope.packet = {
          'start_code': '',
          'sub_start_code': '',
          'message_length': '',
          'dest_uid': '',
          'src_uid': '',
          'transaction_number': '',
          'port_id': '',
          'message_count': '',
          'sub_device': '',
          'command_class': '',
          'param_id': '',
          'response_type': '',
          'nack_reason': '',
          'ack_timer': '',
          'param_data_length': '',
          'param_data': '',
          'checksum': '',
          'actual_size': '',
          'calculated_checksum': '',
          'sub_device_error': false,
          'nack_reason_error': '',
          'ack_timer_error': ''
        };
      };

      resetPacket();

      $scope.reset = function() {
        resetPacket();
        $scope.error = '';
        $scope.packet_data = '';
        $scope.show_output = false;
      };

      $scope.parsePacket = function() {
        resetPacket();
        $scope.error = '';

        var parse_return = parserService.textToBytes($scope.packet_data);
        if (parse_return[0]) {
          $scope.error = 'Invalid packet data: ' + parse_return[0];
          return;
        }
        var packet_data = parse_return[1];
        // Save a copy to work out the checksum later.
        var original_packet_data = packet_data.slice();
        $scope.packet.actual_size = packet_data.length;

        if (packet_data.length >= 1) {
          $scope.packet.start_code = packet_data.shift();
        } else {
          $scope.error = 'Insufficient data for start code';
          return;
        }

        $scope.show_output = true;

        if (packet_data.length >= 1) {
          $scope.packet.sub_start_code = packet_data.shift();
        } else {
          $scope.error = 'Insufficient data for sub start code';
          return;
        }

        if (packet_data.length >= 1) {
          $scope.packet.message_length = packet_data.shift();
        } else {
          $scope.error = 'Insufficient data for message length';
          return;
        }

        if (packet_data.length >= RDM.UID_SIZE) {
          var dst_uid_data = packet_data.slice(0, RDM.UID_SIZE);
          packet_data = packet_data.slice(RDM.UID_SIZE);
          $scope.packet.dest_uid = formatService.arrayToUID(dst_uid_data);
        } else {
          $scope.error = 'Insufficient data for destination UID';
          return;
        }

        if (packet_data.length >= RDM.UID_SIZE) {
          var src_uid_data = packet_data.slice(0, RDM.UID_SIZE);
          packet_data = packet_data.slice(RDM.UID_SIZE);
          $scope.packet.src_uid = formatService.arrayToUID(src_uid_data);
        } else {
          $scope.error = 'Insufficient data for source UID';
          return;
        }

        if (packet_data.length >= 1) {
          $scope.packet.transaction_number = packet_data.shift();
        } else {
          $scope.error = 'Insufficient data for transaction number';
          return;
        }

        // We save port id for later since we need to know the command class to
        // interpret it.
        var port_id;
        if (packet_data.length >= 1) {
          port_id = packet_data.shift();
        } else {
          $scope.error = 'Insufficient data for port ID / response type';
          return;
        }

        if (packet_data.length >= 1) {
          $scope.packet.message_count = packet_data.shift();
        } else {
          $scope.error = 'Insufficient data for message count';
          return;
        }

        var output;  // work around javascript's poor scoping rules
        var hex_value;

        if (packet_data.length >= 2) {
          var sub_device = (packet_data.shift() << 8) + packet_data.shift();
          $scope.packet.sub_device_error =
            !((sub_device === RDM.SUB_DEVICE.ALL_SUB_DEVICES) ||
              ((sub_device >= RDM.SUB_DEVICE.ROOT_DEVICE) &&
               (sub_device <= RDM.SUB_DEVICE_MAX)));
          output = formatService.reverseLookup(RDM.SUB_DEVICE, sub_device);
          hex_value = formatService.toHex(sub_device, 4, '0x');
          if (output) {
            $scope.packet.sub_device = output + ' (' + hex_value + ')';
          } else {
            $scope.packet.sub_device = sub_device + ' (' + hex_value + ')';
          }
        } else {
          $scope.error = 'Insufficient data for sub device';
          return;
        }

        var command_class;
        if (packet_data.length >= 1) {
          command_class = packet_data.shift();
          output =
            formatService.reverseLookup(RDM.COMMAND_CLASS, command_class);
          hex_value = formatService.toHex(command_class, 2, '0x');
          if (output) {
            $scope.packet.command_class = output + ' (' + hex_value + ')';
          } else {
            $scope.packet.command_class = hex_value;
          }
        } else {
          $scope.error = 'Insufficient data for command class';
          return;
        }

        // Now interpret the port id
        if (rdmHelperService.isResponse(command_class)) {
          output = formatService.reverseLookup(RDM.RESPONSE_TYPE, port_id);
          hex_value = formatService.toHex(port_id, 4, '0x');
          if (output) {
            $scope.packet.response_type = output + ' (' + hex_value + ')';
          } else {
            $scope.packet.response_type = hex_value;
          }
        } else {
          $scope.packet.port_id = port_id;
        }

        if (packet_data.length >= 2) {
          var param_id = (packet_data.shift() << 8) + packet_data.shift();
          output = formatService.reverseLookup(RDM.PIDS, param_id);
          hex_value = formatService.toHex(param_id, 4, '0x');

          if (output) {
            $scope.packet.param_id = output + ' (' + hex_value + ')';
          } else {
            $scope.packet.param_id = hex_value;
          }
        } else {
          $scope.error = 'Insufficient data for parameter ID';
          return;
        }

        var param_data_length;
        if (packet_data.length >= 1) {
          param_data_length = packet_data.shift();
          $scope.packet.param_data_length = param_data_length;
        } else {
          $scope.error = 'Insufficient data for parameter data length';
          return;
        }

        if (packet_data.length >= param_data_length) {
          var param_data = packet_data.slice(0, param_data_length);
          packet_data = packet_data.slice(param_data_length);

          if (rdmHelperService.isResponse(command_class) &&
            port_id === RDM.RESPONSE_TYPE.NACK) {
            if (param_data_length === 2) {
              var nack_reason = (param_data[0] << 8) + param_data[1];
              output =
                formatService.reverseLookup(RDM.NACK_REASON, nack_reason);
              hex_value = formatService.toHex(nack_reason, 4, '0x');

              if (output) {
                $scope.packet.nack_reason = output + ' (' + hex_value + ')';
              } else {
                $scope.packet.nack_reason = 'Unknown: ' + hex_value;
              }
            } else {
              $scope.packet.nack_reason_error = 'Parameter data length should' +
                ' be 2';
            }
          } else if (rdmHelperService.isResponse(command_class) &&
            port_id === RDM.RESPONSE_TYPE.ACK_TIMER) {
            if (param_data_length === 2) {
              var ack_timer = (param_data[0] << 8) + param_data[1];
              $scope.packet.ack_timer = ack_timer;
            } else {
              $scope.packet.ack_timer_error = 'Parameter data length should' +
                ' be 2';
            }
          } else {
            $scope.packet.param_data =
              formatService.arrayToHex(param_data, '0x');
          }
        } else {
          $scope.error = 'Insufficient data for parameter data';
          return;
        }

        if (packet_data.length >= 2) {
          var recovered_checksum =
            (packet_data.shift() << 8) + packet_data.shift();
          $scope.packet.checksum =
            formatService.toHex(recovered_checksum, 4, '0x');

          $scope.packet.calculated_checksum = formatService.toHex(
            checksumService.checksumAsValue(original_packet_data.slice(0, -2)),
            4, '0x');
        } else {
          if (packet_data.length) {
            original_packet_data = original_packet_data.slice(0, -1);
          }
          // Checksum was missing
          $scope.packet.calculated_checksum = formatService.toHex(
            checksumService.checksumAsValue(original_packet_data),
            4, '0x');
          packet_data = [];
          return;
        }

        if (packet_data.length !== 0) {
          $scope.error = 'Extra data after checksum';
        }
      };
    }]);
