import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:nextfight/core/presentation/error_message.dart';
import 'package:nextfight/features/auth/application/auth_controller.dart';
import 'package:nextfight/l10n/app_localizations.dart';

class AuthPage extends ConsumerStatefulWidget {
  const AuthPage({super.key});

  @override
  ConsumerState<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends ConsumerState<AuthPage> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _name = TextEditingController();
  bool _registering = false;
  bool _hidePassword = true;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    _name.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final controller = ref.read(authControllerProvider.notifier);
    if (_registering) {
      await controller.register(
        email: _email.text,
        password: _password.text,
        displayName: _name.text,
      );
    } else {
      await controller.login(email: _email.text, password: _password.text);
    }
  }

  @override
  Widget build(BuildContext context) {
    final strings = AppLocalizations.of(context);
    final auth = ref.watch(authControllerProvider);
    ref.listen(authControllerProvider, (_, next) {
      if (next.hasError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(errorMessage(next.error!, strings.genericError)),
          ),
        );
      }
    });
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: AutofillGroup(
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        strings.appName,
                        style: Theme.of(context).textTheme.displaySmall,
                      ),
                      const SizedBox(height: 8),
                      Text(strings.loginSubtitle),
                      const SizedBox(height: 32),
                      if (_registering) ...[
                        TextFormField(
                          controller: _name,
                          textInputAction: TextInputAction.next,
                          autofillHints: const [AutofillHints.name],
                          decoration: InputDecoration(
                            labelText: strings.displayName,
                          ),
                          validator: (value) => (value?.trim().length ?? 0) < 2
                              ? strings.displayName
                              : null,
                        ),
                        const SizedBox(height: 16),
                      ],
                      TextFormField(
                        controller: _email,
                        keyboardType: TextInputType.emailAddress,
                        textInputAction: TextInputAction.next,
                        autofillHints: const [AutofillHints.email],
                        decoration: InputDecoration(labelText: strings.email),
                        validator: (value) =>
                            value != null && value.contains('@')
                            ? null
                            : strings.email,
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _password,
                        obscureText: _hidePassword,
                        autofillHints: const [AutofillHints.password],
                        onFieldSubmitted: (_) => _submit(),
                        decoration: InputDecoration(
                          labelText: strings.password,
                          helperText: _registering
                              ? strings.passwordRequirements
                              : null,
                          suffixIcon: IconButton(
                            tooltip: _hidePassword
                                ? 'Show password'
                                : 'Hide password',
                            onPressed: () =>
                                setState(() => _hidePassword = !_hidePassword),
                            icon: Icon(
                              _hidePassword
                                  ? Icons.visibility
                                  : Icons.visibility_off,
                            ),
                          ),
                        ),
                        validator: (value) =>
                            _registering && (value?.length ?? 0) < 12
                            ? strings.passwordRequirements
                            : (value?.isEmpty ?? true)
                            ? strings.password
                            : null,
                      ),
                      const SizedBox(height: 24),
                      FilledButton(
                        onPressed: auth.isLoading ? null : _submit,
                        child: auth.isLoading
                            ? const SizedBox.square(
                                dimension: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
                              )
                            : Text(
                                _registering
                                    ? strings.createAccount
                                    : strings.signIn,
                              ),
                      ),
                      TextButton(
                        onPressed: auth.isLoading
                            ? null
                            : () =>
                                  setState(() => _registering = !_registering),
                        child: Text(
                          _registering ? strings.signIn : strings.createAccount,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
