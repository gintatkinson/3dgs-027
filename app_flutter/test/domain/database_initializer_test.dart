import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:app_flutter/domain/database_initializer.dart';
import 'package:app_flutter/domain/domain_seed_strategy.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  group('DatabaseInitializer spatial seeding', () {
    test('regenerate assets database', () async {
      final dbPath = 'assets/properties_db.db';
      final file = File(dbPath);
      if (await file.exists()) {
        await file.delete();
      }
      // Inject DomainSeedStrategy to ensure the generated asset is fully populated with mock topology data
      final db = await DatabaseInitializer.create(
        dbPath: dbPath,
        seed: true,
        seedStrategy: DomainSeedStrategy(),
      );
      await db.close();

      final gzFile = File('assets/properties_db.db.gz');
      if (await gzFile.exists()) {
        await gzFile.delete();
      }
      final bytes = await file.readAsBytes();
      final gzipped = gzip.encode(bytes);
      await gzFile.writeAsBytes(gzipped);
      expect(await gzFile.exists(), isTrue);
    });


  });
}
