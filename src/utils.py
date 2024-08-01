from __future__ import annotations
from functools import partial
from typing import Protocol, Callable, Iterable, Awaitable


def compose[A, B, C](f: Callable[A, B], g: Callable[B, C]) -> Callable[A, C]:
    def h(*args, **kwargs) -> C:
        return g(f(*args, **kwargs))

    return h


class Monoid(Protocol):
    @classmethod
    def mempty(cls) -> Monoid: ...

    def mappend(self: Monoid, m: Monoid) -> Monoid: ...


class Functor[A](Protocol):
    def map[A, B](self: Functor[A], f: Callable[A, B]) -> Functor[B]: ...


class Applicative[A](Functor[A], Protocol):
    def apply[A, B](
        self: Applicative[A], f: Applicative[Callable[A, B]]
    ) -> Applicative[B]: ...

    def liftA2[A, B, C](
        self: Applicative[A], f: Callable[A, B, C], fb: Applicative[B]
    ) -> Applicative[C]:
        fb.apply(self.map(f))


class Monad[A](Applicative[A], Protocol):
    def bind[A, B](self: Monad[A], f: Callable[A, Monad[B]]) -> Monad[B]: ...


class Foldable[A](Protocol):
    def fold[A, B](self: Foldable[A], f: Callable[A, B, B], b: B) -> B: ...


class Maybe[A]:
    def __new__(cls, value=None) -> Maybe[A]:
        if value is None:
            return super().__new__(Nothing)
        maybe = super().__new__(Just)
        maybe.value = value
        return maybe

    def __add__(self: Maybe[A], m: Maybe[A]) -> Maybe[A]:
        return self.mappend(m)

    @property
    def is_just[A](self: Maybe[A]) -> bool:
        return isinstance(self, Just)

    @property
    def is_nothing[A](self: Maybe[A]) -> bool:
        return isinstance(self, Nothing)

    @classmethod
    def mempty(cls) -> Maybe[A]:
        return Nothing()

    def mappend(self: Maybe[Monoid[A]], m: Maybe[Monoid[A]]) -> Maybe[Monoid[A]]:
        match (self, m):
            case (Just(value=a1), Just(value=a2)):
                return Just(a1.mappend(a2))
            case (Just(value=a1), Nothing):
                return Just(value=a1)
            case (Nothing, Just(value=a2)):
                return Just(value=a2)
            case _:
                return Nothing()

    def map[A, B](self: Maybe[A], f: Callable[A, B]) -> Maybe[B]:
        try:
            b: B = f(self.value)
        except AttributeError:
            b = None
        except TypeError:
            b: B = partial(f, self.value)
        return Maybe(b)

    def apply[A, B](self: Maybe[A], f: Maybe[Callable[A, B]]) -> Maybe[B]:
        match (self, f):
            case (Just(value=a), Just(value=f)):
                return Maybe(f(a))
            case _:
                return Nothing()

    def bind[A, B](self: Maybe[A], f: Callable[A, Maybe[B]]) -> Maybe[B]:
        match self:
            case Just(value=a):
                return f(a)
            case _:
                return Nothing()

    def fold[A, B](self: Maybe[A], f: Callable[A, B, B], b: B) -> B:
        match self:
            case Just(value=a):
                return f(a, b)
            case _:
                return b


class Just[A](Maybe[A]):
    def __init__(self, value: A) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"Just {self.value}"


class Nothing[A](Maybe[A]):
    def __repr__(self) -> str:
        return self.__class__.__name__


class MList[A](list):
    def __init__(self, iterable: Iterable[A] = None) -> None:
        super().__init__(iterable if iterable is not None else [])

    def __add_(self: MList[A], m: MList[A]) -> MList[A]:
        return self.mappend(m)

    @classmethod
    def mempty(cls) -> MList[A]:
        return MList([])

    def mappend(self: MList[A], m: MList[A]) -> MList[A]:
        return self + m

    def map[A, B](self: MList[A], f: Callable[A, B]) -> MList[B]:
        return [f(a) for a in self]

    async def amap[A, B](self: MList[A], f: Callable[A, Awaitable[B]]) -> MList[B]:
        return [await f(a) for a in self]

    def apply[A, B](self: MList[A], fs: MList[Callable[A, B]]) -> MList[B]:
        return MList(f(a) for f in fs for a in self)

    def bind[A, B](self: MList[A], f: Callable[A, MList[B]]) -> MList[B]:
        return MList(b for lb in (f(a) for a in self) for b in lb)

    def fold[A, B](self: MList[A], f: Callable[[A, B], B], b: B) -> B:
        for a in self:
            b = f(a, b)
        return b


class MDict[T, A](dict):
    def __init__(self, value: dict[T, A] = None) -> None:
        super().__init__(value if value is not None else {})

    def __add__(self: MDict[T, A], m: MDict[T, A]) -> MDict[T, A]:
        return self.mappend(m)

    @classmethod
    def mempty(cls) -> MDict[T, A]:
        return cls()

    def mappend(self: MDict[T, A], m: MDict[T, A]) -> MDict[T, A]:
        return self.update(m)

    def map[A, B](self: MDict[T, A], f: Callable[A, B]) -> MDict[T, B]:
        return MDict({t: f(a) for (t, a) in self.items()})

    def apply[A, B](
        self: MDict[Monoid, A], f: MDict[Monoid, Callable[A, B]]
    ) -> MDict[Monoid, B]:
        d = MDict()
        for m1, a in self.items():
            for m2, f in f.items():
                d[m1.mappend(m2)] = f(a)
        return d

    def bind[A, B](self: MDict[T, A], f: Callable[A, MDict[T, B]]) -> MDict[T, B]:
        d1 = MDict()
        for a in self.values():
            d1.update(f(a))
        return d1

    def fold[A, B](self: MDict[T, A], f: Callable[A, B, B], b: B) -> B:
        for a in self.values():
            b = f(a, b)
        return b


class IO[A]:
    def __init__(self, effect: Callable[A]) -> None:
        self.executed = False
        self.effect = effect
        self.result = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(effect={repr(self.effect)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.effect}"

    def __enter__(self, *args, **kwargs) -> A:
        self()
        return self.result

    def __exit__(self, *args, **kwargs) -> None:
        return

    def __call__(self) -> None:
        if self.executed:
            raise ValueError
        self.result = self.effect()
        self.executed = True

    def map[A, B](self: IO[A], f: Callable[A, B]) -> IO[B]:
        if not self.executed:
            self()
        return IO(f(self.value))

    def apply[A, B](self: IO[A], f: IO[Callable[A, B]]) -> IO[B]:
        if not self.executed:
            self()
        if not f.executed:
            f()
        return IO(f.result(self.result))

    def bind[A, B](self: IO[A], f: Callable[A, IO[B]]) -> IO[B]:
        if not self.executed:
            self()
        io = f(self.result)
        io()
        return io


def ioprint(*args) -> IO[None]:
    return IO(partial(print, *args))


def ioinput(prompt: str) -> IO[str]:
    return IO(partial(input, prompt))


def foo() -> None:
    ioinput("escribe algo: ").bind(ioprint)


class MaybeT[Monad, A]:
    def __init__(
        self, base_monad_cls: Monad, value: A = None
    ) -> MaybeT[Monad[Maybe[A]]]:
        self._base_monad = base_monad_cls
        self.value = base_monad_cls.pure(Maybe(value))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(value={repr(self.value)})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {self.value}"

    @property
    def run_MaybeT(self) -> Monad[Maybe[A]]:
        return self.value

    def map[A, B](self: MaybeT[Monad, A], f: Callable[A, B]) -> MaybeT[Monad, B]:
        match self.run_MaybeT.value.map(f):
            case Just(value=b):
                return MaybeT(self._base_monad, b)
            case _:
                return MaybeT(self._base_monad, None)

    def apply[A, B](
        self: MaybeT[Monad, A], f: MaybeT[Monad, Callable[A, B]]
    ) -> MaybeT[Monad, B]:
        match self.run_MaybeT.map(lambda maybe_a: maybe_a.apply(f.run_MaybeT.value)):
            case self._base_monad(value=Just(value=b)):
                return MaybeT(self._base_monad, b)
            case _:
                return MaybeT(self._base_monad, None)

    def bind[A, B](
        self: MaybeT[Monad, A], f: Callable[A, MaybeT[Monad, B]]
    ) -> MaybeT[Monad, B]:
        match self.run_MaybeT.value:
            case Just(value=a):
                return f(a)
            case _:
                return MaybeT(self._base_monad, None)
