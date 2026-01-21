import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'features/auth/auth_service.dart';
import 'features/auth/login_screen.dart';
import 'features/security/app_security_service.dart';
import 'features/security/lock_screen.dart';
import 'features/weather/weather_card.dart';
import 'features/crops/ui/crop_list_screen.dart';
import 'features/weather/weather_forecast_screen.dart';
import 'features/watering/ui/watering_list_screen.dart';
import 'features/treatments/ui/treatment_history_screen.dart';
import 'features/notifications/services/notification_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase
  await Firebase.initializeApp();
  
  // Initialize Notification Service
  await NotificationService().init();
  
  // Create Security Service and verify access
  final securityService = AppSecurityService();
  await securityService.verifyAccess();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: securityService),
        Provider<AuthService>(create: (_) => AuthService()),
        StreamProvider<User?>(
          create: (context) => context.read<AuthService>().user,
          initialData: null,
        ),
      ],
      child: const FarmalyticsApp(),
    ),
  );
}

class FarmalyticsApp extends StatelessWidget {
  const FarmalyticsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Farmalytics',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D32), // Forest Green
          primary: const Color(0xFF2E7D32),
        ),
      ),
      home: Consumer<AppSecurityService>(
        builder: (context, security, child) {
          // 1. Security Gate (Kill Switch)
          if (security.isLoading) {
            return const Scaffold(
              body: Center(
                child: CircularProgressIndicator(),
              ),
            );
          }

          if (!security.isActive) {
            return LockScreen(message: security.message);
          }

          // 2. Auth Gate
          return Consumer<User?>(
            builder: (context, user, child) {
              if (user == null) {
                return const LoginScreen();
              }
              
              // 3. Dashboard (Home Screen)
              return const DashboardScreen();
            },
          );
        },
      ),
    );
  }
}

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = context.watch<User?>();
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Farmalytics Dashboard'),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthService>().signOut(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const WeatherCard(),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: GridView.count(
                crossAxisCount: 2,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                children: [
                  _FeatureCard(
                    title: 'Crop Management',
                    icon: Icons.eco,
                    color: Colors.green,
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const CropListScreen()),
                    ),
                  ),
                  _FeatureCard(
                    title: 'Weather Forecast',
                    icon: Icons.cloud,
                    color: Colors.blue,
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const WeatherForecastScreen()),
                    ),
                  ),
                  _FeatureCard(
                    title: 'Watering Schedule',
                    icon: Icons.water_drop,
                    color: Colors.cyan,
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const WateringListScreen()),
                    ),
                  ),
                  _FeatureCard(
                    title: 'Treatments',
                    icon: Icons.science,
                    color: Colors.orange,
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const TreatmentHistoryScreen()),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FeatureCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;

  const _FeatureCard({
    required this.title,
    required this.icon,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48, color: color),
            const SizedBox(height: 12),
            Text(
              title,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color.darken(0.2),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

extension on Color {
  Color darken([double amount = .1]) {
    assert(amount >= 0 && amount <= 1);
    final hsv = HSVColor.fromColor(this);
    final darkenedHsv = hsv.withValue((hsv.value - amount).clamp(0.0, 1.0));
    return darkenedHsv.toColor();
  }
}
