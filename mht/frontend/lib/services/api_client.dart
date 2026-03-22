import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiClient {
  static const String baseUrl = 'http://192.168.1.225:8000/api/v1';
  static const storage = FlutterSecureStorage();
  
  static String? jwtToken;
  static String? courseId;

  // Global header generator
  static Map<String, String> get headers {
    if (jwtToken == null) return {'Content-Type': 'application/json'};
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $jwtToken'
    };
  }

  // Auth-specific header
  static Map<String, String> get urlEncodedHeaders => {
    'Content-Type': 'application/x-www-form-urlencoded'
  };
}