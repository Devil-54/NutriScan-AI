/// Plain data holders for Phase 4C dummy content. No backend/API types here -
/// these get replaced by real domain entities once Phase 5 wires the API.
library;

class RecentScanItem {
  const RecentScanItem({
    required this.name,
    required this.healthScore,
    required this.riskLabel,
    required this.dateLabel,
  });

  final String name;
  final int healthScore;
  final String riskLabel;
  final String dateLabel;
}

class RecommendationItem {
  const RecommendationItem({required this.name, required this.reason, required this.icon});

  final String name;
  final String reason;
  final String icon;
}

const List<RecentScanItem> dummyRecentScans = [
  RecentScanItem(name: 'Maggi Noodles', healthScore: 62, riskLabel: 'Moderate Risk', dateLabel: 'Today, 9:41 AM'),
  RecentScanItem(name: 'Diet Coke', healthScore: 41, riskLabel: 'High Risk', dateLabel: 'Yesterday, 6:12 PM'),
  RecentScanItem(name: 'Greek Yogurt', healthScore: 88, riskLabel: 'Safe', dateLabel: 'Yesterday, 8:05 AM'),
];

const List<String> dummyHealthTips = [
  'Drink more water today.',
  'Add a fiber-rich snack between meals.',
  'Check sodium levels before choosing packaged snacks.',
  'A 10-minute walk after meals helps digestion.',
];

const List<RecommendationItem> dummyRecommendations = [
  RecommendationItem(name: 'Oats', reason: 'High fiber, low glycemic index', icon: '🥣'),
  RecommendationItem(name: 'Fresh Fruits', reason: 'Natural sugars, rich in vitamins', icon: '🍎'),
  RecommendationItem(name: 'Roasted Makhana', reason: 'Low sodium, light snack', icon: '🌰'),
];
