import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/constants/route_constants.dart';
import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/theme_provider.dart';
import '../../../../core/utils/responsive_utils.dart';
import '../../../../shared/widgets/custom_app_bar.dart';
import '../../../../shared/widgets/custom_card.dart';
import '../../../../shared/widgets/section_header.dart';
import '../../../../shared/widgets/setting_tile.dart';
import '../../../authentication/presentation/providers/auth_provider.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final maxWidth = ResponsiveUtils.value(context, mobile: double.infinity, tablet: 700.0, desktop: 900.0);
    final themeMode = ref.watch(themeModeProvider);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: const CustomAppBar(title: 'Settings'),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxWidth),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 32),
              children: [
                const SectionHeader(title: 'Preferences'),
                const SizedBox(height: 12),
                CustomCard(
                  child: Column(
                    children: [
                      SettingTile(
                        icon: Icons.dark_mode_outlined,
                        label: 'Dark Mode',
                        trailing: Switch(
                          value: themeMode == ThemeMode.dark,
                          activeThumbColor: AppColors.primary,
                          onChanged: (_) => ref.read(themeModeProvider.notifier).toggle(),
                        ),
                        onTap: () => ref.read(themeModeProvider.notifier).toggle(),
                      ),
                      const Divider(height: 24),
                      SettingTile(icon: Icons.language_rounded, label: 'Language', subtitle: 'English', onTap: () {}),
                      const Divider(height: 24),
                      SettingTile(icon: Icons.notifications_none_rounded, label: 'Notifications', onTap: () {}),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                const SectionHeader(title: 'Data & Privacy'),
                const SizedBox(height: 12),
                CustomCard(
                  child: Column(
                    children: [
                      SettingTile(icon: Icons.lock_outline_rounded, label: 'Privacy', onTap: () {}),
                      const Divider(height: 24),
                      SettingTile(icon: Icons.storage_outlined, label: 'Data & Storage', onTap: () {}),
                      const Divider(height: 24),
                      SettingTile(icon: Icons.file_download_outlined, label: 'Export Report', onTap: () {}),
                      const Divider(height: 24),
                      SettingTile(
                        icon: Icons.delete_outline_rounded,
                        label: 'Delete History',
                        isDestructive: true,
                        onTap: () {},
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                const SectionHeader(title: 'Support'),
                const SizedBox(height: 12),
                CustomCard(
                  child: Column(
                    children: [
                      SettingTile(icon: Icons.help_outline_rounded, label: 'Help & Support', onTap: () {}),
                      const Divider(height: 24),
                      SettingTile(icon: Icons.description_outlined, label: 'Terms', onTap: () {}),
                      const Divider(height: 24),
                      SettingTile(icon: Icons.privacy_tip_outlined, label: 'Privacy Policy', onTap: () {}),
                      const Divider(height: 24),
                      SettingTile(
                        icon: Icons.info_outline_rounded,
                        label: 'About NutriScan',
                        onTap: () => context.goNamed(RouteConstants.aboutName),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                CustomCard(
                  child: SettingTile(
                    icon: Icons.logout_rounded,
                    label: 'Logout',
                    isDestructive: true,
                    onTap: () async {
                      await ref.read(authProvider.notifier).logout();
                      if (context.mounted) context.goNamed(RouteConstants.loginName);
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
