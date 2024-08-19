from PMonad.io import ioinput, ioprint
from PMonad.maybe import Maybe, Just, Nothing
from PMonad.transformers.maybe_t import MaybeT


def validate_word(w: str) -> Maybe[str]:
    return Just(w) if w.startswith("s") else Nothing()


def validate_number(n: str) -> Maybe[str]:
    return Just(n) if n.isdigit() else Nothing()


def main() -> None: (
    MaybeT
    .lift(ioprint("Word validation with MaybeT\n"))
    .then(
        MaybeT(ioinput("Write a word that starts with s: ").map(validate_word))
    )
    .bind(
        lambda word: (
            MaybeT(ioinput("Write a number: ").map(validate_number))
            .bind(
                lambda number: (
                    MaybeT.lift(ioprint(f"{word} {number}"))
                )
            )
        )
    )
)


if __name__ == "__main__":
    main()
