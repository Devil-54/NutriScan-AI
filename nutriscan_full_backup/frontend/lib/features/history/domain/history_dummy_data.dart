import '../../result/domain/result_dummy_data.dart';

/// Immutable personalized snapshot returned by `/scans/history`.
/// The legacy filename is retained so the existing card layout stays stable.
class ScanHistoryEntry {
  const ScanHistoryEntry({
    required this.scanId, required this.name, required this.dateLabel,
    required this.healthScore, required this.riskLevel, required this.ingredients,
    required this.reasons, required this.recommendations, required this.triggeredRules,
    required this.safeFoods, required this.unsafeFoods, required this.profileSnapshot,
    required this.rawOcrText, required this.nutrition,
  });

  final String scanId, name, dateLabel;
  final int healthScore;
  final RiskLevel riskLevel;
  final List<IngredientResult> ingredients;
  final List<String> reasons, recommendations, triggeredRules, safeFoods, unsafeFoods;
  final Map<String, dynamic> profileSnapshot;
  final String? rawOcrText;
  final Map<String, dynamic> nutrition;

  List<IngredientResult> get concernIngredients => ingredients
      .where((ingredient) => ingredient.status != IngredientStatus.safe)
      .toList(growable: false);

  String get personalizedSummary => reasons.isNotEmpty
      ? reasons.first
      : 'Personalized concern: None detected for the saved profile.';

  String get pregnancyContext {
    if (profileSnapshot['pregnant'] != true) return '';
    if (riskLevel == RiskLevel.unsafe || riskLevel == RiskLevel.highRisk) {
      return 'Not Recommended';
    }
    if (riskLevel == RiskLevel.moderateRisk) return 'Use Caution';
    return 'Suitable';
  }

  factory ScanHistoryEntry.fromApi(Map<String, dynamic> json) {
    final rawResult = json['personalized_result'];
    final result = rawResult is Map
        ? Map<String, dynamic>.from(rawResult)
        : const <String, dynamic>{};
    final warnings = ((result['ingredient_warnings'] as List?) ?? const [])
        .whereType<Map>()
        .map((item) => Map<String, dynamic>.from(item))
        .toList(growable: false);
    final risk = result['risk_level']?.toString() ?? 'low';
    final warningNames = warnings
        .map((item) => item['ingredient']?.toString())
        .whereType<String>()
        .toSet();
    final unsafe = _stringList(result['unsafe_ingredients']);
    final safe = _stringList(result['safe_ingredients']);
    final evaluatedIngredients = _stringList(result['ingredients']);
    return ScanHistoryEntry(
      scanId: json['scan_id']?.toString() ?? '',
      name: (json['product_name'] as String?)?.trim().isNotEmpty == true
          ? json['product_name'] as String : json['original_filename']?.toString() ?? 'Unnamed scan',
      dateLabel: _dateLabel(json['created_at']?.toString() ?? ''),
      healthScore: (result['health_score'] as num?)?.round() ?? 0,
      riskLevel: _riskLevel(risk),
      ingredients: [
        for (final warning in warnings) IngredientResult(
          name: warning['ingredient']?.toString() ?? 'Unknown ingredient',
          status: risk == 'critical' || risk == 'high' ? IngredientStatus.danger : IngredientStatus.warning,
          explanation: warning['reason'] as String? ?? 'Personalized concern detected.',
        ),
        for (final ingredient in unsafe)
          if (!warningNames.contains(ingredient)) IngredientResult(
            name: ingredient,
            status: risk == 'critical' || risk == 'high' ? IngredientStatus.danger : IngredientStatus.warning,
            explanation: 'Personalized concern detected.',
          ),
        for (final ingredient in safe.isNotEmpty ? safe : evaluatedIngredients)
          if (!warningNames.contains(ingredient)) IngredientResult(
            name: ingredient, status: IngredientStatus.safe,
            explanation: 'No known risk for your profile at the time of this scan.',
          ),
      ],
      reasons: _stringList(result['reasons']),
      recommendations: _stringList(result['recommendations']),
      triggeredRules: _stringList(result['triggered_rules']),
      safeFoods: safe,
      unsafeFoods: unsafe,
      profileSnapshot: result['profile_snapshot'] == null
          ? const {} : Map<String, dynamic>.from(result['profile_snapshot'] as Map),
      rawOcrText: json['raw_ocr_text'] as String?,
      nutrition: result['nutrition_snapshot'] is Map
          ? Map<String, dynamic>.from(result['nutrition_snapshot'] as Map)
          : const {},
    );
  }
}

List<String> _stringList(Object? value) => value is List
    ? value.map((item) => item?.toString()).whereType<String>().toList(growable: false)
    : const [];

RiskLevel _riskLevel(String value) => switch (value) {
  'critical' => RiskLevel.unsafe, 'high' => RiskLevel.highRisk,
  'moderate' => RiskLevel.moderateRisk, 'low' => RiskLevel.lowRisk,
  _ => RiskLevel.safe,
};

String _dateLabel(String value) {
  final date = DateTime.tryParse(value)?.toLocal();
  if (date == null) return value;
  final hour = date.hour % 12 == 0 ? 12 : date.hour % 12;
  return '${date.day}/${date.month}/${date.year}, $hour:${date.minute.toString().padLeft(2, '0')} ${date.hour >= 12 ? 'PM' : 'AM'}';
}
