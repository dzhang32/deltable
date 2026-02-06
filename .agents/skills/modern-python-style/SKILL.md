---
name: modern-python-style
description: >
  Modern Python 3.13+ code style, type hints, and Google docstrings (without types).
  Enforces PEP 8 layout, PEP 695 generics, built-in generic types, X | Y unions,
  pathlib, dataclasses, and readable idiomatic patterns. Use when writing, reviewing,
  or refactoring Python code, generating Python functions or classes, creating Python
  modules, or when the user mentions Python, .py files, or Python style.
---

# Modern Python Style

Write readable, simple Python 3.13+ code. Follow PEP 8 layout, use modern type hints,
and document with Google-format docstrings that omit types (types belong in annotations).
When in doubt, choose the approach a reader understands in five seconds.

For detailed code examples of every rule below, see [references/examples.md](references/examples.md).

## Guiding Principles

Apply PEP 20 as a decision framework:

- **Explicit over implicit** — annotate signatures, raise specific exceptions, avoid magic.
- **Simple over complex** — if `if/elif` is as clear as `match/case`, use the simpler form.
- **Flat over nested** — use early returns and guard clauses.
- **Readability counts** — optimize for the reader, not the writer.
- **Practicality beats purity** — break any rule when following it hurts readability.

## Code Layout (PEP 8)

- 4 spaces per indent, never tabs.
- 79-character line limit (teams may agree on 99 for code; docstrings/comments stay at 72).
- Wrap long lines inside parentheses/brackets — avoid backslash continuation.
- Break **before** binary operators in multi-line expressions.
- Two blank lines around top-level definitions; one blank line between methods.
- Trailing commas in all multi-line collections, argument lists, and import groups.

### Imports

Place at file top, after module docstring, before constants. One import per line.
Group in order, separated by a blank line:

1. Standard library
2. Third-party packages
3. Local application modules

Use absolute imports. No wildcard imports. Sort lexicographically within each group.

### Whitespace

- Single spaces around `=` in assignments and comparisons.
- No space inside parentheses, before commas, or before call/index brackets.
- No space around `=` in unannotated keyword arguments: `def f(x, verbose=False):`.
- Add space around `=` when annotations are present: `def f(x: int = 0) -> None:`.
- Never align assignments vertically across lines.

## Naming Conventions

| Entity | Convention | Example |
|---|---|---|
| Modules, packages | `snake_case` | `data_loader` |
| Classes, exceptions | `PascalCase` | `DataLoader`, `InvalidTokenError` |
| Functions, methods, variables | `snake_case` | `load_data`, `retry_count` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Type parameters | Short `PascalCase` | `T`, `KeyT` |
| Private/internal | Leading underscore | `_cache`, `_validate()` |

- Never use `l`, `O`, or `I` as single-character names.
- Avoid abbreviations unless universally understood (`url`, `id`, `db` — not `proc_mgr_cfg`).
- Don't encode types in names (`users`, not `users_list`).
- Functions as verb phrases (`calculate_tax`), classes as noun phrases (`HttpClient`), booleans as assertions (`is_valid`).
- Append `Error` to exception class names.

## Type Hints (Python 3.13+)

Annotate **every public function's parameters and return type**. Annotate `-> None` for
side-effect functions. Omit annotations on local variables unless the type cannot be inferred.

### Built-in Generics Only

Never import capitalized aliases from `typing`. Use built-in types directly:

`list[str]`, `dict[str, int]`, `tuple[int, ...]`, `set[float]`, `type[MyClass]`

For abstract types, import from `collections.abc`:

`Sequence`, `Mapping`, `Iterable`, `Callable`, `Iterator`

### Union Syntax

Use `X | Y` — never `Union` or `Optional`:

`str | None`, `str | bytes`, `int | float`

Place `None` last in unions.

### PEP 695 Type Parameters

Declare type parameters inline — never use `TypeVar` or `Generic`:

```python
def first[T](items: Sequence[T]) -> T:
    return items[0]

class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

type Vector = list[float]
type Result[T] = T | Error
```

### Useful Typing Constructs

- `Self` (PEP 673) — methods returning own type.
- `@override` (PEP 698) — mark overridden methods.
- `TypeIs` (PEP 742) — type narrowing (prefer over `TypeGuard`).
- `Final` — constants: `MAX_RETRIES: Final = 3`.
- `Protocol` — structural subtyping / duck-typing with type safety.
- `Literal` — restricted values: `mode: Literal["read", "write"]`.

### When Not to Annotate

- Don't annotate obvious locals (`x = 5`, not `x: int = 5`).
- Don't use `Any` as a crutch — use `object` if truly anything.
- Prefer raising exceptions over returning `None` when possible.

## Docstrings — Google Format Without Types

Use triple double quotes. Types belong **only** in annotations — never in docstrings.

### One-Line Docstrings

Imperative command, ending with a period, on a single line:

```python
def reset_counter() -> None:
    """Reset the global counter to zero."""
```

### Multi-Line Docstrings

Summary line, blank line, extended description, then sections.
Indent section content by 4 spaces. Sections in order: `Args`, `Returns`/`Yields`, `Raises`.

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

### Class Docstrings

Describe what an instance represents. List public attributes in `Attributes` section.
Document `__init__` separately. Use descriptive style for `@property` docstrings.
Omit docstrings on `@override` methods unless behavior differs from parent.

## Modern Python Features to Prefer

### Dataclasses

Use `@dataclass` with `frozen=True`, `slots=True`, `kw_only=True` for data-holding classes:

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class Coordinate:
    latitude: float
    longitude: float
    label: str = ""
```

Use `NamedTuple` for tuple-protocol compatibility. Plain classes for complex init logic.

### pathlib Over os.path

Use `pathlib.Path` for all filesystem operations:

```python
config = Path.home() / ".config" / "myapp" / "settings.toml"
config.parent.mkdir(parents=True, exist_ok=True)
for py_file in Path("src").rglob("*.py"):
    process(py_file)
```

### Structural Pattern Matching

Use `match`/`case` for destructuring nested data, `isinstance` chains, or dictionary shapes.
Don't use it for simple value comparisons where `if/elif` is equally clear.

### Exception Groups

Use `except*` with `asyncio.TaskGroup` or batch operations — not as a replacement for
regular `except`.

### F-Strings

Prefer f-strings for all string formatting. Python 3.12+ allows nested quotes, backslashes,
and multi-line expressions inside braces.

## Function Design and Error Handling

- Keep functions short and focused — one task per function.
- Use early returns and guard clauses over deep nesting.
- Catch specific exceptions, never bare `except:`.
- Keep `try` blocks minimal — wrap only code that might raise.
- Use `raise X from Y` for exception chaining.
- Use context managers (`with`) for all resource management.
- Never use mutable default arguments — use `None` sentinel pattern.
- Every branch must either return a value or raise — never mix return with implicit `None`.

## Anti-Patterns to Avoid

- Don't assign lambdas to variables — use `def`.
- Don't concatenate strings with `+` in loops — use `"".join()`.
- Don't use `os.path` — use `pathlib`.
- Don't import from `typing` what exists as a built-in generic.
- Don't compare booleans with `==` — use truthiness directly.
- Don't use `type()` for type checks — use `isinstance()`.
- Don't use `len(x) == 0` — use `not x`.
- Test identity with `is`/`is not` for singletons: `if x is None:`.
