class AuthUser {
  const AuthUser({
    required this.id,
    required this.email,
    required this.displayName,
    required this.role,
  });

  factory AuthUser.fromJson(Map<String, dynamic> json) => AuthUser(
    id: json['id'] as String,
    email: json['email'] as String,
    displayName: json['display_name'] as String,
    role: json['role'] as String,
  );

  final String id;
  final String email;
  final String displayName;
  final String role;

  Map<String, dynamic> toJson() => {
    'id': id,
    'email': email,
    'display_name': displayName,
    'role': role,
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

  Map<String, dynamic> toJson() => {
    'access_token': accessToken,
    'refresh_token': refreshToken,
    'user': user.toJson(),
  };
}
