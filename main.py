from typing_extensions import Self
from src.core.security import PasswordHasher


class Singleton:
  _instance = None

  def __new__(cls, *args, **kwargs) -> Self:
    if cls._instance is None:
      cls._instance = super().__new__(cls, *args, **kwargs)
    return cls._instance


def main():
  print("Hello from library-management-system!")

  singletons = [Singleton() for _ in range(10000)]

  print(
    "All same:",
    all(
      hash(singletons[0]) == hash(s) and id(singletons[0]) == id(s) for s in singletons
    ),
  )

  phs = [PasswordHasher for _ in range(100)]
  print(
    "All same:",
    all(
      hash(phs[0]) == hash(ph)
      and id(phs[0]) == id(ph)
      and hash(phs[0]._hasher) == hash(ph._hasher)
      and id(phs[0]._hasher) == id(ph._hasher)
      for ph in phs
    ),
  )

  def print_hash(x):
    print(f"{id(x)=}, {hash(x)=}")

  print_hash(phs[0])
  print_hash(phs[0]._hasher)
  print_hash(phs[1])
  print_hash(phs[1]._hasher)

  

if __name__ == "__main__":
  main()
