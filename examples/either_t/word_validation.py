from PMonad.io import IO, ioinput, ioprint
from PMonad.either import Either, Left, Right
from PMonad.transformers.either_t import EitherT


def validate_word(w: str) -> Either[str, str]:
    return Right(w) if w.startswith("s") else Left("Word does not start with 's'")


def validate_number(n: str) -> Either[str, str]:
    return Right(n) if n.isdigit() else Left("Not a number")


def main() -> None: (
    EitherT
    .lift(ioprint("Word validation with EitherT"))
    .then(
        EitherT(
            ioinput("Write a word that starts with s: ")
            .map(validate_word)
        )
    )
    .bind(
        lambda word: (
            EitherT(
                ioinput("Write a number: ")
                .map(validate_number)
            )
            .bind(
                lambda number: (
                    EitherT.lift(IO(result=f"{word} {number}"))
                )
            )
        )
    )
    .run()
    .bind(lambda e: ioprint(e.value))
)


if __name__ == "__main__":
    main()
