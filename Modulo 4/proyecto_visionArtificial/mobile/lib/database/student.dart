class Student {
  final String id;
  final String name;
  final String career;
  final String controlNumber;

  Student({
    required this.id,
    required this.name,
    required this.career,
    required this.controlNumber,
  });

  factory Student.fromMap(Map<String, dynamic> map) {
    return Student(
      id: map['id'],
      name: map['name'],
      career: map['career'],
      controlNumber: map['control_number'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'career': career,
      'control_number': controlNumber,
    };
  }
}
