import 'package:flutter/material.dart';
import 'package:nextfight/core/presentation/view_state.dart';

class AsyncStateView<T> extends StatelessWidget {
  const AsyncStateView({
    required this.state,
    required this.successBuilder,
    super.key,
  });
  final ViewState<T> state;
  final Widget Function(BuildContext, T, bool) successBuilder;

  @override
  Widget build(BuildContext context) => switch (state) {
    LoadingState<T>() => const Center(child: CircularProgressIndicator()),
    EmptyState<T>() => const _Status(
      icon: Icons.inbox_outlined,
      label: 'No content available',
    ),
    OfflineState<T>() => const _Status(
      icon: Icons.cloud_off_outlined,
      label: 'You are offline',
    ),
    FailureState<T>(:final message) => _Status(
      icon: Icons.error_outline,
      label: message,
    ),
    SuccessState<T>(:final data, :final isStale) => successBuilder(
      context,
      data,
      isStale,
    ),
  };
}

class _Status extends StatelessWidget {
  const _Status({required this.icon, required this.label});
  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) => Semantics(
    liveRegion: true,
    label: label,
    child: Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 40),
          const SizedBox(height: 12),
          Text(label, textAlign: TextAlign.center),
        ],
      ),
    ),
  );
}
