from typing import Callable


def identity[A](a: A) -> A:
    return a


def const[A, B](a: A) -> A:
    def f(b: B) -> A:
        return a
    return f


def compose[A, B, C](f: Callable[A, B], g: Callable[B, C]) -> Callable[A, C]:
    def h(*args, **kwargs) -> C:
        return g(f(*args, **kwargs))

    return h
