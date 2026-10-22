class UserModel {
  const UserModel({required this.userId, required this.name, required this.email, required this.isVerified});

  final String userId;
  final String name;
  final String email;
  final bool isVerified;

  factory UserModel.fromJson(Map<String, dynamic> json) => UserModel(
        userId: json['user_id'] as String,
        name: json['name'] as String,
        email: json['email'] as String,
        isVerified: json['is_verified'] as bool? ?? false,
      );
}
