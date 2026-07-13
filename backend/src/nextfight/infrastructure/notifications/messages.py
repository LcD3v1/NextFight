"""Localized transactional push message catalog."""

from nextfight.infrastructure.database.entities import FightStatus


def localized_state_message(locale: str, state: FightStatus) -> tuple[str, str]:
    """Return a state-triggered alert in the user's preferred language."""
    portuguese = locale.casefold().startswith("pt")
    messages = {
        FightStatus.NEXT: (
            ("Sua luta é a próxima", "A luta anterior terminou. Prepare-se!")
            if portuguese
            else ("Your fight is next", "The previous fight ended. Get ready!")
        ),
        FightStatus.WALKOUTS: (
            ("Entradas iniciadas", "Os atletas estão a caminho do octógono.")
            if portuguese
            else ("Walkouts started", "The athletes are heading to the cage.")
        ),
    }
    return messages[state]


def localized_lead_message(locale: str, minutes: int) -> tuple[str, str]:
    """Return a prediction-based advance warning in the preferred language."""
    if locale.casefold().startswith("pt"):
        return (
            "Sua luta está se aproximando",
            f"A previsão indica início em aproximadamente {minutes} minutos.",
        )
    return (
        "Your fight is approaching",
        f"The current prediction indicates a start in about {minutes} minutes.",
    )


def localized_card_message(locale: str) -> tuple[str, str]:
    """Return a card-order change notification in the preferred language."""
    if locale.casefold().startswith("pt"):
        return (
            "O card do evento mudou",
            "A ordem das lutas foi atualizada. Confira a nova posição da sua luta.",
        )
    return (
        "The event card changed",
        "The fight order was updated. Check your fight's new position.",
    )
