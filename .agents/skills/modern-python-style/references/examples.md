# Code Examples Reference

Detailed examples for every rule in the Modern Python Style skill.

## Code Layout

### Line wrapping — break before operators

```python
# ✅ Correct
total = (
    gross_wages
    + taxable_interest
    + (dividends - qualified_dividends)
    - ira_deduction
)

# ❌ Wrong — break after operator
total = (
    gross_wages +
    taxable_interest +
    (dividends - qualified_dividends) -
    ira_deduction
)
```

### Import ordering

```python
# ✅ Correct grouping and order
import os
import sys
from pathlib import Path

import httpx
from pydantic import BaseModel

from myapp.core import Engine
from myapp.utils import retry
```

### Trailing commas

```python
# ✅ Clean diffs with trailing commas
names = [
    "Alice",
    "Bob",
    "Charlie",
]

def create_user(
    name: str,
    email: str,
    role: str = "viewer",
) -> User:
    ...
```

## Type Hints

### Built-in generics vs legacy imports

```python
# ✅ Modern 3.13+
def process(items: list[str]) -> dict[str, int]:
    ...

def transform(data: tuple[int, ...]) -> set[float]:
    ...

# ❌ Never in 3.13+
from typing import List, Dict, Tuple, Set
def process(items: List[str]) -> Dict[str, int]:
    ...
```

### Abstract types from collections.abc

```python
# ✅ Correct source
from collections.abc import Sequence, Mapping, Callable, Iterator

def search(items: Sequence[str], predicate: Callable[[str], bool]) -> Iterator[str]:
    return (item for item in items if predicate(item))

# ❌ Wrong source
from typing import Sequence, Callable, Iterator
```

### Union syntax

```python
# ✅ Modern
def find_user(user_id: int) -> User | None:
    ...

def parse(value: str | bytes) -> dict[str, object]:
    ...

# ❌ Legacy
from typing import Optional, Union
def find_user(user_id: int) -> Optional[User]:
    ...
```

### PEP 695 type parameters

```python
# ✅ Modern inline type parameters
def first[T](items: Sequence[T]) -> T:
    return items[0]

def merge[K, V](a: dict[K, V], b: dict[K, V]) -> dict[K, V]:
    return {**a, **b}

class Registry[T]:
    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def register(self, name: str, item: T) -> None:
        self._items[name] = item

    def get(self, name: str) -> T | None:
        return self._items.get(name)

# ✅ Type aliases with the type statement
type Vector = list[float]
type Matrix = list[Vector]
type Result[T] = T | Error
type Handler[T] = Callable[[T], None]

# ✅ Bounded type parameters
type Comparable = int | float | str
def maximum[T: Comparable](a: T, b: T) -> T:
    return a if a >= b else b

# ❌ Old style — never use in 3.13+
from typing import TypeVar, Generic
T = TypeVar("T")
class Registry(Generic[T]):
    ...
```

### Useful typing constructs

```python
from typing import Final, Self, override
from typing import TypeIs, Protocol, Literal

# Self for fluent interfaces
class Builder:
    def with_name(self, name: str) -> Self:
        self._name = name
        return self

# @override for method overrides
class Animal:
    def speak(self) -> str:
        return ""

class Dog(Animal):
    @override
    def speak(self) -> str:
        return "woof"

# TypeIs for type narrowing
def is_string_list(val: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(x, str) for x in val)

# Protocol for structural subtyping
class Drawable(Protocol):
    def draw(self, x: int, y: int) -> None: ...

# Literal for restricted values
def open_file(path: Path, mode: Literal["r", "w", "a"] = "r") -> TextIO:
    ...

# Final for constants
MAX_RETRIES: Final = 3
```

## Docstrings — Google Format Without Types

### One-line docstring

```python
def reset_counter() -> None:
    """Reset the global counter to zero."""
    global _counter
    _counter = 0
```

### Full function docstring

```python
def fetch_rows(
    table: Table,
    keys: Sequence[str],
    require_all: bool = False,
) -> Mapping[str, tuple[str, ...]]:
    """Fetch rows from a database table by key.

    Retrieve rows for the given keys. String keys are UTF-8
    encoded before lookup. Missing keys are silently skipped
    unless require_all is set.

    Args:
        table: An open database table instance.
        keys: Keys identifying the rows to fetch.
        require_all: If True, raise if any key is missing.

    Returns:
        A mapping of keys to row data, where each row is a
        tuple of column values.

    Raises:
        KeyError: If require_all is True and a key is missing.
        ConnectionError: If the database connection is lost.
    """
```

### Class docstring with attributes and __init__

```python
class Customer:
    """A customer account with billing information.

    Attributes:
        name: The customer's display name.
        email: The primary contact email address.
        balance: Current account balance in cents.
    """

    def __init__(self, name: str, email: str, balance: int = 0) -> None:
        """Initialize a customer account.

        Args:
            name: The customer's display name.
            email: The primary contact email address.
            balance: Starting balance in cents.
        """
        self.name = name
        self.email = email
        self.balance = balance
```

### Generator docstring with Yields

```python
def paginate[T](items: Sequence[T], page_size: int = 20) -> Iterator[Sequence[T]]:
    """Yield successive pages from a sequence.

    Args:
        items: The full collection to paginate.
        page_size: Maximum items per page.

    Yields:
        A subsequence of up to page_size items.
    """
    for i in range(0, len(items), page_size):
        yield items[i : i + page_size]
```

### Property docstring

```python
class Circle:
    """A circle defined by its radius."""

    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def area(self) -> float:
        """The area of the circle."""
        return math.pi * self._radius ** 2
```

## Modern Features

### Frozen slotted dataclasses

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True, kw_only=True)
class Coordinate:
    latitude: float
    longitude: float
    label: str = ""

@dataclass(slots=True, kw_only=True)
class Config:
    host: str = "localhost"
    port: int = 8080
    tags: list[str] = field(default_factory=list)
```

### pathlib for all filesystem operations

```python
from pathlib import Path

# Building paths
config = Path.home() / ".config" / "myapp" / "settings.toml"
config.parent.mkdir(parents=True, exist_ok=True)

# Reading and writing
content = config.read_text(encoding="utf-8")
config.write_text(new_content, encoding="utf-8")

# Globbing
for py_file in Path("src").rglob("*.py"):
    process(py_file)

# Walking directory trees (3.12+)
for root, dirs, files in Path("src").walk():
    for name in files:
        print(root / name)

# Checking paths
if config.exists() and config.is_file():
    ...
```

### Structural pattern matching

```python
# ✅ Good use — destructuring and type dispatch
match event:
    case KeyPress(key="q"):
        quit_app()
    case Click(position=(x, y)) if x > 100:
        handle_click(x, y)
    case {"action": "login", "user": username}:
        authenticate(username)
    case _:
        log_unhandled(event)

# ❌ Overkill — simple if/elif is clearer
match status:
    case "ok":
        handle_ok()
    case "error":
        handle_error()
# ✅ Just use if/elif for simple value checks
if status == "ok":
    handle_ok()
elif status == "error":
    handle_error()
```

### Exception groups with asyncio

```python
import asyncio

async def run_tasks() -> None:
    """Run concurrent tasks, handling errors per type."""
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch_data())
            tg.create_task(send_notification())
    except* ConnectionError as eg:
        for err in eg.exceptions:
            log_connection_failure(err)
    except* ValueError as eg:
        for err in eg.exceptions:
            log_validation_error(err)
```

### F-string features (3.12+)

```python
# Nested quotes — no workarounds needed
message = f"User {user.name!r} has {len(user.items)} items"

# Multi-line expressions
query = f"""
    SELECT *
    FROM users
    WHERE name = {"admin" if is_admin else username}
"""
```

## Function Design

### Early returns over deep nesting

```python
# ✅ Flat with guard clauses
def process_payment(order: Order) -> Receipt:
    """Process payment for an order.

    Args:
        order: The order to process.

    Returns:
        A receipt for the completed payment.

    Raises:
        ValueError: If the order is empty or total is non-positive.
    """
    if not order.items:
        raise ValueError("Order has no items")
    if order.total <= 0:
        raise ValueError("Order total must be positive")
    return _charge_and_generate_receipt(order)

# ❌ Deeply nested
def process_payment(order: Order) -> Receipt:
    if order.items:
        if order.total > 0:
            return _charge_and_generate_receipt(order)
        else:
            raise ValueError("Order total must be positive")
    else:
        raise ValueError("Order has no items")
```

### Mutable default argument — None sentinel

```python
# ✅ Correct
def append_to(element: int, target: list[int] | None = None) -> list[int]:
    """Append an element to a list, creating one if not provided.

    Args:
        element: The integer to append.
        target: The list to append to. Creates a new list if None.

    Returns:
        The list with the element appended.
    """
    if target is None:
        target = []
    target.append(element)
    return target

# ❌ Bug — mutable default shared across calls
def append_to(element: int, target: list[int] = []) -> list[int]:
    target.append(element)
    return target
```

### Exception handling

```python
# ✅ Specific exceptions, minimal try block, chaining
def load_config(path: Path) -> Config:
    """Load configuration from a TOML file.

    Args:
        path: Path to the configuration file.

    Returns:
        The parsed configuration.

    Raises:
        ConfigError: If the file cannot be loaded or parsed.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"Config not found: {path}") from exc

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML in {path}") from exc

    return Config(**data)
```

### Context managers for resources

```python
# ✅ Always use with for resource management
with open(path, encoding="utf-8") as f:
    content = f.read()

with db.transaction():
    db.execute(query)
```
