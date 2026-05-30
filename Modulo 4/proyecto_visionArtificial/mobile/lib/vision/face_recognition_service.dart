import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/services.dart';
import 'package:google_mlkit_face_detection/google_mlkit_face_detection.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

class RecognitionResult {
  final String label;
  final double confidence;

  RecognitionResult({required this.label, required this.confidence});
}

class FaceRecognitionService {
  late Interpreter _interpreter;
  late List<String> _labels;

  static const int inputSize = 160;

  Future<void> loadModel() async {
    _interpreter = await Interpreter.fromAsset('assets/model/model.tflite');

    final labelsJson = await rootBundle.loadString('assets/model/labels.json');
    final Map<String, dynamic> labelsMap = jsonDecode(labelsJson);

    _labels = List.filled(labelsMap.length, '');

    labelsMap.forEach((key, value) {
      _labels[value] = key;
    });
  }

  Future<RecognitionResult?> recognizeFace(String imagePath, Face face) async {
    final bytes = await File(imagePath).readAsBytes();
    final originalImage = img.decodeImage(bytes);

    if (originalImage == null) return null;

    final box = face.boundingBox;

    final marginX = (box.width * 0.35).round();
    final marginY = (box.height * 0.35).round();

    final x = (box.left.round() - marginX).clamp(0, originalImage.width - 1);
    final y = (box.top.round() - marginY).clamp(0, originalImage.height - 1);

    final right = (box.right.round() + marginX).clamp(0, originalImage.width);
    final bottom = (box.bottom.round() + marginY).clamp(
      0,
      originalImage.height,
    );

    final w = (right - x).clamp(1, originalImage.width - x);
    final h = (bottom - y).clamp(1, originalImage.height - y);

    final croppedFace = img.copyCrop(
      originalImage,
      x: x,
      y: y,
      width: w,
      height: h,
    );

    final resizedFace = img.copyResize(
      croppedFace,
      width: inputSize,
      height: inputSize,
    );

    final input = Float32List(1 * inputSize * inputSize * 3);
    int index = 0;

    for (int row = 0; row < inputSize; row++) {
      for (int col = 0; col < inputSize; col++) {
        final pixel = resizedFace.getPixel(col, row);

        input[index++] = pixel.r.toDouble();
        input[index++] = pixel.g.toDouble();
        input[index++] = pixel.b.toDouble();
      }
    }

    final output = List.generate(1, (_) => List.filled(_labels.length, 0.0));

    _interpreter.run(input.reshape([1, inputSize, inputSize, 3]), output);

    final probabilities = output[0];

    int bestIndex = 0;
    double bestScore = probabilities[0];

    for (int i = 1; i < probabilities.length; i++) {
      if (probabilities[i] > bestScore) {
        bestScore = probabilities[i];
        bestIndex = i;
      }
    }

    return RecognitionResult(label: _labels[bestIndex], confidence: bestScore);
  }

  void dispose() {
    _interpreter.close();
  }
}
