import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:farmalytics/features/auth/signup_screen.dart';
import 'package:farmalytics/features/auth/auth_service.dart';
import 'package:provider/provider.dart';
import 'package:mocktail/mocktail.dart';

class MockAuthService extends Mock implements AuthService {}

void main() {
  testWidgets('SignupScreen displays basic UI elements', (WidgetTester tester) async {
    final mockAuth = MockAuthService();
    await tester.pumpWidget(MaterialApp(
      home: Provider<AuthService>.value(
        value: mockAuth,
        child: const SignupScreen(),
      ),
    ));

    expect(find.text('Create Account'), findsNWidgets(2));
    expect(find.text('Full Name'), findsOneWidget);
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.byType(ElevatedButton), findsOneWidget);
  });

  testWidgets('Validation error shown on empty signup', (WidgetTester tester) async {
    final mockAuth = MockAuthService();
    await tester.pumpWidget(MaterialApp(
      home: Provider<AuthService>.value(
        value: mockAuth,
        child: const SignupScreen(),
      ),
    ));

    await tester.pumpAndSettle();
    
    final signupButton = find.byType(ElevatedButton);
    expect(signupButton, findsOneWidget);
    await tester.tap(signupButton);
    await tester.pumpAndSettle();

    expect(find.text('Enter your name'), findsOneWidget);
    expect(find.text('Enter your email'), findsOneWidget);
    expect(find.text('Enter your password'), findsOneWidget);
  });
}
