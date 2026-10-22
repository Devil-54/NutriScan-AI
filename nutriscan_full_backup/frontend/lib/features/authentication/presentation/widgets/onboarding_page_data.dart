import 'package:flutter/material.dart';

class OnboardingPageData {
  const OnboardingPageData({required this.icon, required this.title, required this.description});

  final IconData icon;
  final String title;
  final String description;
}

const List<OnboardingPageData> onboardingPages = [
  OnboardingPageData(
    icon: Icons.document_scanner_rounded,
    title: 'Scan packaged food instantly.',
    description: 'Point your camera at any ingredient label and let NutriScan read it in seconds.',
  ),
  OnboardingPageData(
    icon: Icons.psychology_alt_rounded,
    title: 'Understand ingredients with AI.',
    description: 'We break down every ingredient, additive, and allergen so nothing stays hidden.',
  ),
  OnboardingPageData(
    icon: Icons.favorite_rounded,
    title: 'Receive personalized health recommendations.',
    description: 'Get guidance tailored to your health profile - conditions, allergies, and goals.',
  ),
];
