import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:farmalytics/features/auth/login_screen.dart';
import 'package:farmalytics/features/auth/auth_service.dart';
import 'package:provider/provider.dart';
import 'package:mocktail/mocktail.dart';

class MockAuthService extends Mock implements AuthService {}

void main() {
  testWidgets('LoginScreen displays basic UI elements', (WidgetTester tester) async {
    final mockAuth = MockAuthService();
    await tester.pumpWidget(MaterialApp(
      home: Provider<AuthService>.value(
        value: mockAuth,
        child: const LoginScreen(),
      ),
    ));

    expect(find.text('Welcome Back'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.byType(ElevatedButton), findsOneWidget);
  });

  testWidgets('Validation error shown on empty login', (WidgetTester tester) async {
    final mockAuth = MockAuthService();
    await tester.pumpWidget(MaterialApp(
      home: Provider<AuthService>.value(
        value: mockAuth,
        child: const LoginScreen(),
      ),
    ));

    await tester.pumpAndSettle();

    final loginButton = find.byType(ElevatedButton);
    expect(loginButton, findsOneWidget);
    
    await tester.tap(loginButton);
    await tester.pumpAndSettle();

    expect(find.text('Enter your email'), findsOneWidget);
    expect(find.text('Enter your password'), findsOneWidget);
  });
}
