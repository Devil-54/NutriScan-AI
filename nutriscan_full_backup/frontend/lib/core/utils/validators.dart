class Validators {
  Validators._();

  static final RegExp _emailPattern = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

  static String? email(String? value) {
    if (value == null || value.trim().isEmpty) return 'Email is required';
    if (!_emailPattern.hasMatch(value.trim())) return 'Enter a valid email address';
    return null;
  }

  /// Mirrors the backend's password policy (min 8 chars, upper+lower+digit)
  /// so users get instant feedback instead of a round-trip 400 response.
  static String? password(String? value) {
    if (value == null || value.isEmpty) return 'Password is required';
    if (value.length < 8) return 'Password must be at least 8 characters';
    if (!value.contains(RegExp(r'[A-Z]'))) return 'Include at least one uppercase letter';
    if (!value.contains(RegExp(r'[a-z]'))) return 'Include at least one lowercase letter';
    if (!value.contains(RegExp(r'[0-9]'))) return 'Include at least one digit';
    return null;
  }

  static String? required(String? value, {String fieldName = 'This field'}) {
    if (value == null || value.trim().isEmpty) return '$fieldName is required';
    return null;
  }

  static String? Function(String?) confirmPassword(String Function() getOriginal) {
    return (value) {
      if (value == null || value.isEmpty) return 'Please confirm your password';
      if (value != getOriginal()) return 'Passwords do not match';
      return null;
    };
  }
}
