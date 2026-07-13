class AuthUser {
  const AuthUser({
    required this.id,
    required this.email,
    required this.displayName,
    required this.role,
    this.locale = 'en',
    this.timezone = 'UTC',
  });

  factory AuthUser.fromJson(Map<String, dynamic> json) => AuthUser(
    id: json['id'] as String,
    email: json['email'] as String,
    displayName: json['display_name'] as String,
    role: json['role'] as String,
    locale: json['locale'] as String? ?? 'en',
    timezone: json['timezone'] as String? ?? 'UTC',
  );

  final String id;
  final String email;
  final String displayName;
  final String role;
  final String locale;
  final String timezone;

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'display_name': displayName,
    'role': role,
    'locale': locale,
    'timezone': timezone,
  };
}

class AuthSession {
  const AuthSession({
    required this.accessToken,
    required this.refreshToken,
    required this.user,
  });

  factory AuthSession.fromJson(Map<String, dynamic> json) => AuthSession(
    accessToken: json['access_token'] as String,
    refreshToken: json['refresh_token'] as String,
    user: AuthUser.fromJson(json['user'] as Map<String, dynamic>),
  );

  final String accessToken;
  final String refreshToken;
  final AuthUser user;

  AuthSession withUser(AuthUser replacement) => AuthSession(
    accessToken: accessToken,
    refreshToken: refreshToken,
    user: replacement,
  );

  Map<String, dynamic> toJson() => {
    'access_token': accessToken,
    'refresh_token': refreshToken,
    'user': user.toJson(),
  };
}
