import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import 'vision/face_detector_service.dart';
import 'vision/face_recognition_service.dart';
import 'database/student.dart';
import 'database/student_database.dart';

List<CameraDescription> cameras = [];

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  cameras = await availableCameras();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Reconocimiento de Alumnos',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(useMaterial3: true),
      home: const CameraScreen(),
    );
  }
}

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;

  final FaceDetectorService _faceDetector = FaceDetectorService();
  final FaceRecognitionService _recognizer = FaceRecognitionService();

  bool _isCameraReady = false;
  bool _isDetecting = false;

  int _facesFound = 0;

  String _recognizedLabel = 'Sin reconocimiento';
  double _confidence = 0.0;

  Student? _student;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    final frontCamera = cameras.firstWhere(
      (camera) => camera.lensDirection == CameraLensDirection.front,
      orElse: () => cameras.first,
    );

    _controller = CameraController(
      frontCamera,
      ResolutionPreset.medium,
      enableAudio: false,
    );

    await _controller!.initialize();

    // Cargar modelo TFLite
    await _recognizer.loadModel();

    if (!mounted) return;

    setState(() {
      _isCameraReady = true;
    });
  }

  Future<void> _detectFace() async {
    if (_controller == null ||
        !_controller!.value.isInitialized ||
        _isDetecting) {
      return;
    }

    setState(() {
      _isDetecting = true;
    });

    try {
      final photo = await _controller!.takePicture();

      final faces = await _faceDetector.detectFromFile(photo.path);

      if (!mounted) return;

      if (faces.isEmpty) {
        setState(() {
          _facesFound = 0;
          _recognizedLabel = 'No se detectó rostro';
          _confidence = 0.0;
          _student = null;
        });
        return;
      }

      final result = await _recognizer.recognizeFace(photo.path, faces.first);

      if (!mounted) return;

      if (result != null) {
        Student? student;

        if (result.confidence >= 0.40) {
          student = await StudentDatabase.instance.getStudentById(result.label);
        }

        if (!mounted) return;

        setState(() {
          _facesFound = faces.length;
          _confidence = result.confidence;

          if (result.confidence >= 0.50 && student != null) {
            _recognizedLabel = result.label;
            _student = student;
          } else {
            _recognizedLabel = 'Alumno no reconocido';
            _student = null;
          }
        });
      } else {
        setState(() {
          _facesFound = faces.length;
          _recognizedLabel = 'No reconocido';
          _confidence = 0.0;
          _student = null;
        });
      }
    } catch (e) {
      debugPrint('Error detectando/reconociendo rostro: $e');
    } finally {
      if (mounted) {
        setState(() {
          _isDetecting = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    _faceDetector.dispose();
    _recognizer.dispose();
    StudentDatabase.instance.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isCameraReady || _controller == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Reconocimiento Facial'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(child: Center(child: CameraPreview(_controller!))),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Text(
                  'Rostros detectados: $_facesFound',
                  style: const TextStyle(fontSize: 18),
                ),

                const SizedBox(height: 8),

                Text(
                  'Alumno: $_recognizedLabel',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),

                const SizedBox(height: 4),

                Text(
                  'Confianza: ${(_confidence * 100).toStringAsFixed(2)}%',
                  style: const TextStyle(fontSize: 16),
                ),

                if (_student != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    'Nombre: ${_student!.name}',
                    style: const TextStyle(fontSize: 16),
                  ),
                  Text(
                    'Carrera: ${_student!.career}',
                    style: const TextStyle(fontSize: 16),
                  ),
                  Text(
                    'No. Control: ${_student!.controlNumber}',
                    style: const TextStyle(fontSize: 16),
                  ),
                ],

                const SizedBox(height: 16),

                ElevatedButton(
                  onPressed: _isDetecting ? null : _detectFace,
                  child: Text(
                    _isDetecting ? 'Detectando...' : 'Detectar y reconocer',
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
