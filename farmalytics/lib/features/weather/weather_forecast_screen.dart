import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'weather_service.dart';

class WeatherForecastScreen extends StatelessWidget {
  const WeatherForecastScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Weather Forecast'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
      ),
      body: FutureBuilder<WeatherData>(
        future: WeatherService().fetchWeather(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }

          final weather = snapshot.data!;
          return SingleChildScrollView(
            child: Column(
              children: [
                _buildCurrentSummary(weather),
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      '7-Day Outlook',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: weather.forecast.length,
                  separatorBuilder: (context, index) => const Divider(height: 1),
                  itemBuilder: (context, index) {
                    final day = weather.forecast[index];
                    return _buildForecastTile(day);
                  },
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCurrentSummary(WeatherData weather) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.blue.shade700, Colors.blue.shade400],
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
        ),
      ),
      child: Column(
        children: [
          const Icon(Icons.cloud, size: 80, color: Colors.white),
          const SizedBox(height: 16),
          Text(
            '${weather.temperature.round()}°C',
            style: const TextStyle(fontSize: 64, color: Colors.white, fontWeight: FontWeight.bold),
          ),
          Text(
            weather.condition,
            style: const TextStyle(fontSize: 24, color: Colors.white70),
          ),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _SummaryItem(icon: Icons.water_drop, label: 'Humidity', value: '${weather.humidity.round()}%'),
              _SummaryItem(icon: Icons.air, label: 'Wind', value: '${weather.windSpeed.round()} km/h'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildForecastTile(ForecastDay day) {
    final bool isRainy = day.condition.toLowerCase().contains('rain');

    return ListTile(
      leading: Icon(
        isRainy ? Icons.umbrella : Icons.wb_sunny,
        color: isRainy ? Colors.blue : Colors.orange,
      ),
      title: Text(DateFormat('EEEE, MMM dd').format(day.date)),
      subtitle: Text(day.condition),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            '${day.maxTemp.round()}°',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          Text(
            '${day.minTemp.round()}°',
            style: const TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

class _SummaryItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _SummaryItem({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(color: Colors.white54, fontSize: 12)),
        Text(value, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ],
    );
  }
}
