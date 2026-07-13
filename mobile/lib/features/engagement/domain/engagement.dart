class Favorite {
  const Favorite({
    required this.id,
    required this.targetType,
    required this.targetId,
    required this.createdAt,
  });

  factory Favorite.fromJson(Map<String, dynamic> json) => Favorite(
    id: json['id'] as String,
    targetType: json['target_type'] as String,
    targetId: json['target_id'] as String,
    createdAt: DateTime.parse(json['created_at'] as String),
  );

  final String id;
  final String targetType;
  final String targetId;
  final DateTime createdAt;
}

class FightAlert {
  const FightAlert({
    required this.id,
    required this.fightId,
    required this.triggerType,
    required this.status,
    required this.createdAt,
    this.leadMinutes,
  });

  factory FightAlert.fromJson(Map<String, dynamic> json) => FightAlert(
    id: json['id'] as String,
    fightId: json['fight_id'] as String,
    triggerType: json['trigger_type'] as String,
    status: json['status'] as String,
    createdAt: DateTime.parse(json['created_at'] as String),
    leadMinutes: json['lead_minutes'] as int?,
  );

  final String id;
  final String fightId;
  final String triggerType;
  final String status;
  final DateTime createdAt;
  final int? leadMinutes;
}
