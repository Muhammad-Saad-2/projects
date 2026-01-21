import 'package:flutter/material.dart';
import 'weather_service.dart';

class WeatherCard extends StatelessWidget {
  const WeatherCard({super.key});

  @override
  Widget build(BuildContext context) {
    final weatherService = WeatherService();

    return FutureBuilder<WeatherData>(
      future: weatherService.fetchWeather(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const _WeatherLoadingCard();
        }

        if (snapshot.hasError) {
          return _WeatherErrorCard(error: snapshot.error.toString());
        }

        if (!snapshot.hasData) {
          return const SizedBox.shrink();
        }

        final data = snapshot.data!;
        return Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF2E7D32), Color(0xFF43A047)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                color: Colors.green.withOpacity(0.3),
                blurRadius: 12,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${data.temperature.round()}°C',
                      style: const TextStyle(
                        fontSize: 48,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      data.condition,
                      style: const TextStyle(
                        fontSize: 18,
                        color: Colors.white70,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(Icons.water_drop_outlined, color: Colors.white70, size: 16),
                        const SizedBox(width: 4),
                        Text(
                          'Humidity: ${data.humidity}%',
                          style: const TextStyle(color: Colors.white70),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              _getWeatherIcon(data.condition),
            ],
          ),
        );
      },
    );
  }

  Widget _getWeatherIcon(String condition) {
    IconData iconData;
    final cond = condition.toLowerCase();
    
    if (cond.contains('clear')) {
      iconData = Icons.wb_sunny_rounded;
    } else if (cond.contains('cloudy') || cond.contains('mainly clear')) {
      iconData = Icons.wb_cloudy_rounded;
    } else if (cond.contains('rain') || cond.contains('drizzle') || cond.contains('shower')) {
      iconData = Icons.umbrella_rounded;
    } else if (cond.contains('thunderstorm')) {
      iconData = Icons.thunderstorm_rounded;
    } else if (cond.contains('snow')) {
      iconData = Icons.ac_unit_rounded;
    } else {
      iconData = Icons.cloud_rounded;
    }

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        shape: BoxShape.circle,
      ),
      child: Icon(
        iconData,
        size: 60,
        color: Colors.white,
      ),
    );
  }
}

class _WeatherLoadingCard extends StatelessWidget {
  const _WeatherLoadingCard();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      height: 140,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(24),
      ),
      child: const Center(
        child: CircularProgressIndicator(color: Color(0xFF2E7D32)),
      ),
    );
  }
}

class _WeatherErrorCard extends StatelessWidget {
  final String error;
  const _WeatherErrorCard({required this.error});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.red[100]!),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Colors.red),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              'Weather unavailable: $error',
              style: TextStyle(color: Colors.red[900], fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }
}
// Fixed the BoxShape typo in a separate tool call if needed or just correct it here.
// I'll correct it in-place in this tool call.
