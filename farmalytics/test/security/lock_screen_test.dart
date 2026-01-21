import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:farmalytics/features/security/lock_screen.dart';

void main() {
  testWidgets('LockScreen displays the provided message', (WidgetTester tester) async {
    const testMessage = 'Your access has been revoked.';
    
    await tester.pumpWidget(const MaterialApp(
      home: LockScreen(message: testMessage),
    ));

    expect(find.text('Access Denied'), findsOneWidget);
    expect(find.text(testMessage), findsOneWidget);
    expect(find.byIcon(Icons.lock_person_rounded), findsOneWidget);
  });
}
