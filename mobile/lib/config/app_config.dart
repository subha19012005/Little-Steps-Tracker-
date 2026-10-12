/// Central API configuration for Little Steps Tracker.
///
/// When your development machine changes IP address, update [baseUrl] here.
/// This is the ONLY place you need to change the server address.
class AppConfig {
  AppConfig._(); // prevent instantiation

  /// Base URL of the local FastAPI development server.
  /// Format: `http://YOUR-MACHINE-IPv4:8000`
  static const String baseUrl = 'http://10.103.161.250:8000';
}
