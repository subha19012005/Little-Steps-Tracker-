import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

class QrDisplayScreen extends StatelessWidget {
  final String childId;

  // Regex: valid Child ID must be CH- followed by exactly 6 alphanumeric chars
  static final RegExp _validPattern = RegExp(r'^CH-[A-Za-z0-9]{6}$');

  const QrDisplayScreen({super.key, required this.childId});

  /// Returns true only when childId is non-empty and matches CH-XXXXXX
  bool get _isValid =>
      childId.trim().isNotEmpty && _validPattern.hasMatch(childId.trim());

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Child QR Code'),
      ),
      body: Center(
        child: _isValid ? _buildQrView() : _buildInvalidView(),
      ),
    );
  }

  // ─── Valid: show QR code + readable ID ───────────────────────────────────

  Widget _buildQrView() {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // QR code encodes ONLY the childId string
          QrImageView(
            data: childId.trim(),
            version: QrVersions.auto,
            size: 250.0,
          ),

          const SizedBox(height: 24),

          // Small grey label
          const Text(
            'Child ID',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey,
            ),
          ),

          const SizedBox(height: 4),

          // The actual ID displayed in bold below the QR code
          Text(
            childId.trim(),
            style: const TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
        ],
      ),
    );
  }

  // ─── Invalid / empty: show a friendly message instead of crashing ─────────

  Widget _buildInvalidView() {
    final String message = childId.trim().isEmpty
        ? 'No Child ID was provided.\nPlease register a child first.'
        : 'The Child ID "$childId" is not valid.\nExpected format: CH-XXXXXX';

    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.warning_amber_rounded,
            size: 64,
            color: Colors.orange,
          ),

          const SizedBox(height: 24),

          const Text(
            'Cannot Display QR Code',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),

          const SizedBox(height: 12),

          Text(
            message,
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: 15,
              color: Colors.grey,
            ),
          ),
        ],
      ),
    );
  }
}
