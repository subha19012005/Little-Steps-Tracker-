import 'package:dio/dio.dart';
import 'package:flutter/material.dart';

class ChildRegistrationScreen extends StatefulWidget {
  const ChildRegistrationScreen({super.key});

  @override
  State<ChildRegistrationScreen> createState() =>
      _ChildRegistrationScreenState();
}

class _ChildRegistrationScreenState
    extends State<ChildRegistrationScreen> {
  final nameController = TextEditingController();
  final centreController = TextEditingController();

  DateTime? selectedDate;
  String? selectedGender;
  bool isLoading = false;

  final Dio dio = Dio();

  Future<void> selectDate() async {
    final pickedDate = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2015),
      lastDate: DateTime.now(),
    );

    if (pickedDate != null) {
      setState(() {
        selectedDate = pickedDate;
      });
    }
  }

  Future<void> registerChild() async {
    if (nameController.text.trim().isEmpty ||
        selectedDate == null ||
        selectedGender == null ||
        centreController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please fill all the details'),
        ),
      );
      return;
    }

    setState(() {
      isLoading = true;
    });

    try {
      final response = await dio.post(
        'http://10.220.122.166:8000/api/children',
        data: {
          'name': nameController.text.trim(),
          'date_of_birth':
              '${selectedDate!.year.toString().padLeft(4, '0')}-'
              '${selectedDate!.month.toString().padLeft(2, '0')}-'
              '${selectedDate!.day.toString().padLeft(2, '0')}',
          'gender': selectedGender,
          'centre': centreController.text.trim(),
        },
      );

      if (!mounted) return;

      final data = response.data;

      showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            title: const Text('Child Registered'),
            content: Text(
              'Child ID: ${data['child_id']}\n\n'
              'Name: ${data['name']}\n'
              'Gender: ${data['gender']}\n'
              'Centre: ${data['centre']}',
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: const Text('OK'),
              ),
            ],
          );
        },
      );
    } on DioException catch (e) {
      if (!mounted) return;

      String message = 'Could not register child.';

      if (e.response != null) {
        message = 'Server error: ${e.response?.statusCode}';
      } else {
        message = 'Could not connect to the backend.';
      }

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    nameController.dispose();
    centreController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Register Child'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Child Registration',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Enter the child details below.',
              style: TextStyle(
                fontSize: 16,
              ),
            ),
            const SizedBox(height: 30),
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'Child Name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            InkWell(
              onTap: selectDate,
              child: InputDecorator(
                decoration: const InputDecoration(
                  labelText: 'Date of Birth',
                  border: OutlineInputBorder(),
                ),
                child: Text(
                  selectedDate == null
                      ? 'Select date'
                      : '${selectedDate!.day}/${selectedDate!.month}/${selectedDate!.year}',
                ),
              ),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: selectedGender,
              decoration: const InputDecoration(
                labelText: 'Gender',
                border: OutlineInputBorder(),
              ),
              items: const [
                DropdownMenuItem(
                  value: 'Male',
                  child: Text('Male'),
                ),
                DropdownMenuItem(
                  value: 'Female',
                  child: Text('Female'),
                ),
              ],
              onChanged: (value) {
                setState(() {
                  selectedGender = value;
                });
              },
            ),
            const SizedBox(height: 16),
            TextField(
              controller: centreController,
              decoration: const InputDecoration(
                labelText: 'Centre',
                hintText: 'Enter centre name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 30),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: isLoading ? null : registerChild,
                child: isLoading
                    ? const SizedBox(
                        height: 24,
                        width: 24,
                        child: CircularProgressIndicator(),
                      )
                    : const Text(
                        'Register Child',
                        style: TextStyle(fontSize: 16),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}