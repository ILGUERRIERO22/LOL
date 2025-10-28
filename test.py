"""Simple command-line calculator script."""

from __future__ import annotations

import operator
from typing import Callable, Dict

Operation = Callable[[float, float], float]

OPERATIONS: Dict[str, Operation] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}


def calculate(lhs: float, op: str, rhs: float) -> float:
    """Return the result of applying *op* between *lhs* and *rhs*.

    Raises:
        ValueError: If the operator is not supported or if a division by zero is attempted.
    """

    if op not in OPERATIONS:
        raise ValueError(f"Operatore non supportato: {op}")

    if op == "/" and rhs == 0:
        raise ValueError("Divisione per zero non permessa")

    return OPERATIONS[op](lhs, rhs)


def main() -> None:
    print("Calcolatrice semplice. Inserisci espressioni nel formato: numero operatore numero")
    print("Operatori disponibili: +, -, *, /")
    print("Digita 'esci' per terminare.")

    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "esci":
            print("Arrivederci!")
            break

        parts = user_input.split()
        if len(parts) != 3:
            print("Formato non valido. Usa: numero operatore numero")
            continue

        left_str, op, right_str = parts
        try:
            left = float(left_str.replace(",", "."))
            right = float(right_str.replace(",", "."))
            result = calculate(left, op, right)
        except ValueError as exc:
            print(f"Errore: {exc}")
            continue
        except ZeroDivisionError:
            print("Errore: divisione per zero")
            continue

        if result.is_integer():
            print(int(result))
        else:
            print(result)


if __name__ == "__main__":
    main()
