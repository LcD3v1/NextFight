class OrganizationSummary {
  const OrganizationSummary({
    required this.id,
    required this.name,
    required this.slug,
    this.logoUrl,
  });

  factory OrganizationSummary.fromJson(Map<String, dynamic> json) =>
      OrganizationSummary(
        id: json['id'] as String,
        name: json['name'] as String,
        slug: json['slug'] as String,
        logoUrl: json['logo_url'] as String?,
      );

  final String id;
  final String name;
  final String slug;
  final String? logoUrl;
}

class AthleteSummary {
  const AthleteSummary({
    required this.id,
    required this.name,
    this.nickname,
    this.countryCode,
    this.imageUrl,
  });

  factory AthleteSummary.fromJson(Map<String, dynamic> json) => AthleteSummary(
    id: json['id'] as String,
    name: json['name'] as String,
    nickname: json['nickname'] as String?,
    countryCode: json['country_code'] as String?,
    imageUrl: json['image_url'] as String?,
  );

  final String id;
  final String name;
  final String? nickname;
  final String? countryCode;
  final String? imageUrl;
}

class Fight {
  const Fight({
    required this.id,
    required this.eventId,
    required this.redAthlete,
    required this.blueAthlete,
    required this.currentOrder,
    required this.roundsScheduled,
    required this.status,
    this.weightClass,
    this.boutType,
    this.actualStartAt,
    this.actualEndAt,
    this.resultMethod,
    this.winnerAthleteId,
  });

  factory Fight.fromJson(Map<String, dynamic> json) => Fight(
    id: json['id'] as String,
    eventId: json['event_id'] as String,
    redAthlete: AthleteSummary.fromJson(
      json['red_athlete'] as Map<String, dynamic>,
    ),
    blueAthlete: AthleteSummary.fromJson(
      json['blue_athlete'] as Map<String, dynamic>,
    ),
    currentOrder: json['current_order'] as int,
    roundsScheduled: json['rounds_scheduled'] as int,
    status: json['status'] as String,
    weightClass: json['weight_class'] as String?,
    boutType: json['bout_type'] as String?,
    actualStartAt: _date(json['actual_start_at']),
    actualEndAt: _date(json['actual_end_at']),
    resultMethod: json['result_method'] as String?,
    winnerAthleteId: json['winner_athlete_id'] as String?,
  );

  final String id;
  final String eventId;
  final AthleteSummary redAthlete;
  final AthleteSummary blueAthlete;
  final int currentOrder;
  final int roundsScheduled;
  final String status;
  final String? weightClass;
  final String? boutType;
  final DateTime? actualStartAt;
  final DateTime? actualEndAt;
  final String? resultMethod;
  final String? winnerAthleteId;
}

class FightEvent {
  const FightEvent({
    required this.id,
    required this.name,
    required this.slug,
    required this.scheduledStartAt,
    required this.status,
    required this.organization,
    this.venue,
    this.city,
    this.countryCode,
    this.actualStartAt,
    this.fights = const [],
  });

  factory FightEvent.fromJson(Map<String, dynamic> json) => FightEvent(
    id: json['id'] as String,
    name: json['name'] as String,
    slug: json['slug'] as String,
    scheduledStartAt: DateTime.parse(json['scheduled_start_at'] as String),
    status: json['status'] as String,
    organization: OrganizationSummary.fromJson(
      json['organization'] as Map<String, dynamic>,
    ),
    venue: json['venue'] as String?,
    city: json['city'] as String?,
    countryCode: json['country_code'] as String?,
    actualStartAt: _date(json['actual_start_at']),
    fights: (json['fights'] as List<dynamic>? ?? const [])
        .map((item) => Fight.fromJson(item as Map<String, dynamic>))
        .toList(growable: false),
  );

  final String id;
  final String name;
  final String slug;
  final DateTime scheduledStartAt;
  final String status;
  final OrganizationSummary organization;
  final String? venue;
  final String? city;
  final String? countryCode;
  final DateTime? actualStartAt;
  final List<Fight> fights;

  bool get isLive => status == 'live';
}

DateTime? _date(dynamic value) =>
    value is String ? DateTime.parse(value) : null;
