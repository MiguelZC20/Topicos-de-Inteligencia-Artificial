import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

import 'student.dart';

class StudentDatabase {
  static final StudentDatabase instance = StudentDatabase._init();

  static Database? _database;

  StudentDatabase._init();

  Future<Database> get database async {
    if (_database != null) return _database!;

    _database = await _initDB('students.db');
    return _database!;
  }

  Future<Database> _initDB(String filePath) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(path, version: 1, onCreate: _createDB);
  }

  Future<void> _createDB(Database db, int version) async {
    await db.execute('''
      CREATE TABLE students (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        career TEXT NOT NULL,
        control_number TEXT NOT NULL
      )
    ''');

    await _insertInitialData(db);
  }

  Future<void> _insertInitialData(Database db) async {
    final students = [
      Student(
        id: 'alumno_01',
        name: 'Raul Fernando Canizales Lizarraga',
        career: 'Ingeniería Electrica',
        controlNumber: '25170133',
      ),
      Student(
        id: 'alumno_02',
        name: 'Jael Orlando Ortiz Lugo',
        career: 'Ingeniería Mecanica',
        controlNumber: '24170409',
      ),
      Student(
        id: 'alumno_03',
        name: 'David Fernando Mendoza Hernandez',
        career: 'Ingeniería Electronica',
        controlNumber: '18100012',
      ),
      Student(
        id: 'alumno_04',
        name: 'Hugo Castro Bernal',
        career: 'Ingeniería Mecanica',
        controlNumber: '20170396',
      ),
      Student(
        id: 'alumno_05',
        name: 'Kevin Rafael Camacho Ledesma',
        career: 'Ingeniería en Sistemas',
        controlNumber: '20170873',
      ),
      Student(
        id: 'alumno_06',
        name: 'María Fernanda Alcalá Palominos',
        career: 'Ingeniería Ambiental',
        controlNumber: '20170386',
      ),
      Student(
        id: 'alumno_07',
        name: 'Yahir Alexander Zazueta Torres',
        career: 'Ingeniería en Sistemas',
        controlNumber: '20171551',
      ),
      Student(
        id: 'alumno_08',
        name: 'Carlos Ivan Cervantes Araujo',
        career: 'Ingeniería en Sistemas',
        controlNumber: '21171271',
      ),
      Student(
        id: 'alumno_09',
        name: 'Jose Martin Valles Garcia',
        career: 'Ingeniería Bioquimica',
        controlNumber: '20170301',
      ),
      Student(
        id: 'alumno_10',
        name: 'Dereck Jesus Quintero Urrea',
        career: 'Ingeniería en Sistemas',
        controlNumber: '21170442',
      ),
      Student(
        id: 'alumno_11',
        name: 'Angel Calderon Sandoval',
        career: 'Ingeniería en Sistemas',
        controlNumber: '23170105',
      ),
      Student(
        id: 'alumno_12',
        name: 'Pablo Daniel Ponce Lopez',
        career: 'Ingeniería en Sistemas',
        controlNumber: '20170783',
      ),
      Student(
        id: 'alumno_13',
        name: 'Francisco Javier Cazares Ibarra',
        career: 'Ingeniería en Sistemas',
        controlNumber: '21170285',
      ),
      Student(
        id: 'alumno_14',
        name: 'Felipe Ortega Ibarra',
        career: 'Ingeniería en Gestion Empresarial',
        controlNumber: '22170413',
      ),
      Student(
        id: 'alumno_15',
        name: 'Luis Jose Felix Audelo',
        career: 'Ingeniería Electronica',
        controlNumber: '24171263',
      ),
      Student(
        id: 'alumno_16',
        name: 'Miguel Angel Zavala Carmona',
        career: 'Ingeniería en Sistemas',
        controlNumber: '20170872',
      ),
    ];

    for (final student in students) {
      await db.insert('students', student.toMap());
    }
  }

  Future<Student?> getStudentById(String id) async {
    final db = await instance.database;

    final result = await db.query(
      'students',
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );

    if (result.isEmpty) return null;

    return Student.fromMap(result.first);
  }

  Future<void> close() async {
    final db = await instance.database;
    db.close();
  }
}
