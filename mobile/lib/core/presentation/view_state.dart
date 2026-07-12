sealed class ViewState<T> {
  const ViewState();
}

final class LoadingState<T> extends ViewState<T> {
  const LoadingState();
}

final class EmptyState<T> extends ViewState<T> {
  const EmptyState();
}

final class OfflineState<T> extends ViewState<T> {
  const OfflineState();
}

final class FailureState<T> extends ViewState<T> {
  const FailureState(this.message);
  final String message;
}

final class SuccessState<T> extends ViewState<T> {
  const SuccessState(this.data, {this.isStale = false});
  final T data;
  final bool isStale;
}
