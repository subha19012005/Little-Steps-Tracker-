import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../config/app_config.dart';

// ─── Error categories ─────────────────────────────────────────────────────────

enum _ErrorKind {
  /// Scanned value does not match CH-XXXXXX format.
  invalidFormat,

  /// Backend returned HTTP 404 — ID is valid but not in the database.
  notFound,

  /// Device cannot reach the server (connection refused / timeout).
  connectionError,

  /// Backend returned HTTP 5xx or an unexpected error.
  serverError,
}

// ─── Data model for a child returned by the backend ──────────────────────────

class ChildDetails {
  final String childId;
  final String name;
  final String dateOfBirth;
  final String gender;
  final String centre;

  const ChildDetails({
    required this.childId,
    required this.name,
    required this.dateOfBirth,
    required this.gender,
    required this.centre,
  });

  factory ChildDetails.fromJson(Map<String, dynamic> json) {
    return ChildDetails(
      childId: json['child_id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      dateOfBirth: json['date_of_birth']?.toString() ?? '',
      gender: json['gender']?.toString() ?? '',
      centre: json['centre']?.toString() ?? '',
    );
  }
}

// ─── Scanner screen ───────────────────────────────────────────────────────────

class QrScannerScreen extends StatefulWidget {
  const QrScannerScreen({super.key});

  @override
  State<QrScannerScreen> createState() => _QrScannerScreenState();
}

class _QrScannerScreenState extends State<QrScannerScreen> {
  // Camera controller
  final MobileScannerController _controller = MobileScannerController();

  // Dio HTTP client — reuse across requests
  final Dio _dio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ),
  );

  // Regex: CH- followed by exactly 6 alphanumeric characters
  final RegExp _childIdPattern = RegExp(r'^CH-[A-Za-z0-9]{6}$');

  // ── State ──────────────────────────────────────────────────────────────────

  /// True once a barcode has been captured and is being processed.
  /// Prevents duplicate detections while showing a result or loading.
  bool _isProcessing = false;

  /// True while the HTTP request to the backend is in flight.
  bool _isLoading = false;

  /// Populated on a successful backend fetch.
  ChildDetails? _childDetails;

  /// Set when any error occurs — drives the error panel UI.
  String? _errorMessage;

  /// Categorises the error so the UI can show distinct titles and icons.
  _ErrorKind? _errorKind;

  // ── Barcode detection ──────────────────────────────────────────────────────

  void _onDetect(BarcodeCapture capture) {
    if (_isProcessing) return;

    final barcodes = capture.barcodes;
    if (barcodes.isEmpty) return;

    final String? rawValue = barcodes.first.rawValue;
    if (rawValue == null || rawValue.trim().isEmpty) return;

    final String scanned = rawValue.trim();

    // Lock further detections immediately
    setState(() {
      _isProcessing = true;
    });

    _controller.stop();

    if (_childIdPattern.hasMatch(scanned)) {
      // Format is valid — fetch real details from the backend
      _fetchChildDetails(scanned);
    } else {
      // Format is wrong — no network call needed
      setState(() {
        _errorKind = _ErrorKind.invalidFormat;
        _errorMessage =
            'The scanned QR code does not contain a valid Child ID.\n'
            'Expected format: CH-XXXXXX';
      });
    }
  }

  // ── Backend fetch ──────────────────────────────────────────────────────────

  Future<void> _fetchChildDetails(String childId) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _childDetails = null;
    });

    try {
      final response = await _dio.get(
        '${AppConfig.baseUrl}/api/children/$childId',
      );

      if (!mounted) return;

      setState(() {
        _childDetails = ChildDetails.fromJson(
          Map<String, dynamic>.from(response.data as Map),
        );
        _isLoading = false;
      });
    } on DioException catch (e) {
      if (!mounted) return;

      // Diagnostic log — visible in `flutter run` terminal
      debugPrint('[QrScanner] DioException type=${e.type} '
          'status=${e.response?.statusCode} '
          'url=${e.requestOptions.uri}');

      final _ErrorKind kind;
      final String message;

      final int? status = e.response?.statusCode;

      if (status == 404) {
        // Backend confirmed the ID does not exist
        kind = _ErrorKind.notFound;
        message = 'This QR code is not registered in the system.\n'
            'Child ID: $childId';
      } else if (e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        // Device could not reach the server at all
        kind = _ErrorKind.connectionError;
        message = 'Could not connect to the server.\n'
            'Make sure the backend is running and your phone\n'
            'is on the same Wi-Fi as your computer.';
      } else {
        // HTTP 500 or any other unexpected server-side error
        kind = _ErrorKind.serverError;
        message = 'The server returned an unexpected error.\n'
            'Status: ${status ?? "unknown"}. Please try again.';
      }

      setState(() {
        _errorKind = kind;
        _errorMessage = message;
        _isLoading = false;
      });
    }
  }

  // ── Reset ──────────────────────────────────────────────────────────────────

  void _scanAgain() {
    setState(() {
      _isProcessing = false;
      _isLoading = false;
      _childDetails = null;
      _errorMessage = null;
      _errorKind = null;
    });
    _controller.start();
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // ── Build ──────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Child QR Code'),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (!_isProcessing) return _buildScanner();
    if (_isLoading) return _buildLoadingPanel();
    if (_childDetails != null) return _buildDetailsPanel();
    return _buildErrorPanel();
  }

  // ── Live camera ────────────────────────────────────────────────────────────

  Widget _buildScanner() {
    return Stack(
      children: [
        MobileScanner(
          controller: _controller,
          onDetect: _onDetect,
          errorBuilder: (context, error) {
            return _buildCameraError(error);
          },
        ),
        Align(
          alignment: Alignment.bottomCenter,
          child: Container(
            width: double.infinity,
            color: Colors.black54,
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
            child: const Text(
              'Point the camera at a Child QR code to scan',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white, fontSize: 14),
            ),
          ),
        ),
      ],
    );
  }

  // ── Loading ────────────────────────────────────────────────────────────────

  Widget _buildLoadingPanel() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 24),
          Text(
            'Fetching child details...',
            style: TextStyle(fontSize: 16, color: Colors.grey),
          ),
        ],
      ),
    );
  }

  // ── Child details ──────────────────────────────────────────────────────────

  Widget _buildDetailsPanel() {
    final child = _childDetails!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              const Icon(Icons.check_circle, color: Colors.green, size: 32),
              const SizedBox(width: 12),
              const Text(
                'Child Found',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Details card
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  _detailRow(Icons.badge_outlined, 'Child ID', child.childId),
                  const Divider(height: 24),
                  _detailRow(Icons.person_outline, 'Name', child.name),
                  const Divider(height: 24),
                  _detailRow(
                    Icons.cake_outlined,
                    'Date of Birth',
                    child.dateOfBirth,
                  ),
                  const Divider(height: 24),
                  _detailRow(
                    Icons.wc_outlined,
                    'Gender',
                    child.gender,
                  ),
                  if (child.centre.isNotEmpty) ...[
                    const Divider(height: 24),
                    _detailRow(
                      Icons.location_on_outlined,
                      'Centre',
                      child.centre,
                    ),
                  ],
                ],
              ),
            ),
          ),

          const SizedBox(height: 32),

          // Scan Again button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _scanAgain,
              icon: const Icon(Icons.qr_code_scanner),
              label: const Text('Scan Again', style: TextStyle(fontSize: 16)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _detailRow(IconData icon, String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 22, color: Colors.blueGrey),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 2),
              Text(
                value.isEmpty ? '—' : value,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ── Error ──────────────────────────────────────────────────────────────────

  Widget _buildErrorPanel() {
    // ── Choose title, icon and colour based on error kind ────────────────────
    final IconData icon;
    final Color iconColor;
    final String title;

    switch (_errorKind) {
      case _ErrorKind.invalidFormat:
        icon = Icons.qr_code_2;
        iconColor = Colors.orange;
        title = 'Invalid Child QR Code';
        break;
      case _ErrorKind.notFound:
        icon = Icons.person_search;
        iconColor = Colors.deepOrange;
        title = 'Child Not Found';
        break;
      case _ErrorKind.connectionError:
        icon = Icons.wifi_off;
        iconColor = Colors.blueGrey;
        title = 'Could Not Connect to Server';
        break;
      case _ErrorKind.serverError:
        icon = Icons.cloud_off;
        iconColor = Colors.red;
        title = 'Server Error';
        break;
      case null:
        icon = Icons.error_outline;
        iconColor = Colors.red;
        title = 'Something Went Wrong';
        break;
    }

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 72, color: iconColor),
            const SizedBox(height: 24),
            Text(
              title,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: iconColor,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              _errorMessage ?? 'An unexpected error occurred.',
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 15),
            ),
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _scanAgain,
                icon: const Icon(Icons.qr_code_scanner),
                label:
                    const Text('Scan Again', style: TextStyle(fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Camera error ───────────────────────────────────────────────────────────

  Widget _buildCameraError(MobileScannerException error) {
    String message;
    switch (error.errorCode) {
      case MobileScannerErrorCode.permissionDenied:
        message =
            'Camera permission was denied.\n'
            'Please allow camera access in your device settings.';
        break;
      case MobileScannerErrorCode.unsupported:
        message = 'Your device does not support QR code scanning.';
        break;
      default:
        message = 'Could not start the camera. Please try again.';
    }
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.camera_alt, size: 64, color: Colors.grey),
            const SizedBox(height: 24),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 15, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }
}
