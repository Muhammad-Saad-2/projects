import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:farmalytics/features/weather/weather_service.dart';
import 'package:geolocator/geolocator.dart';

class MockHttpClient extends Mock implements http.Client {}

void main() {
  group('WeatherData Model', () {
    test('WeatherData.fromJson creates valid object', () {
      final json = {
        'current': {
          'temperature_2m': 25.5,
          'relative_humidity_2m': 60,
          'weather_code': 0,
          'wind_speed_10m': 12.5,
        },
        'daily': {
          'time': ['2026-01-21'],
          'temperature_2m_max': [30.0],
          'temperature_2m_min': [20.0],
          'weather_code': [0],
        }
      };

      final weather = WeatherData.fromJson(json);

      expect(weather.temperature, 25.5);
      expect(weather.humidity, 60);
      expect(weather.condition, 'Clear sky');
      expect(weather.windSpeed, 12.5);
      expect(weather.forecast.length, 1);
      expect(weather.forecast.first.maxTemp, 30.0);
    });

    test('Condition mapping handles Various codes', () {
      expect(WeatherData.fromJson({'current': {'weather_code': 61}}).condition, 'Rainy');
      expect(WeatherData.fromJson({'current': {'weather_code': 95}}).condition, 'Thunderstorm');
      expect(WeatherData.fromJson({'current': {'weather_code': -1}}).condition, 'Unknown');
    });
  });
}
