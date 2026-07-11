"""
generate_all_content.py

Management command to:
1. Add rich Markdown content to all lessons using a programmatic content generator
2. Set appropriate lesson types (PDF vs VIDEO)
3. Create quizzes for all modules
"""

from django.core.management.base import BaseCommand
from courses.models import Course, Module, Lesson, Quiz, QuizQuestion, QuizChoice

IMAGE_MAP = {
    "abstract": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&q=80",
    "ai": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&q=80",
    "analytics": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
    "api": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80",
    "automation": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&q=80",
    "brainstorm": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=800&q=80",
    "brand": "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=800&q=80",
    "business": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
    "camera": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&q=80",
    "chart": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
    "cli": "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=800&q=80",
    "cloud": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
    "code": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&q=80",
    "color": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=800&q=80",
    "component": "https://images.unsplash.com/photo-1555099962-4199c345e5dd?w=800&q=80",
    "composition": "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800&q=80",
    "content": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800&q=80",
    "copywriting": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=800&q=80",
    "dashboard": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
    "data": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
    "decorators": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80",
    "design": "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=800&q=80",
    "docker": "https://images.unsplash.com/photo-1605745341112-85968b19335b?w=800&q=80",
    "editing": "https://images.unsplash.com/photo-1527856263665-4648e85f3f90?w=800&q=80",
    "email": "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=800&q=80",
    "figma": "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?w=800&q=80",
    "finance": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "functions": "https://images.unsplash.com/photo-1515879218367-8466d910y1984?w=800&q=80",
    "growth": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&q=80",
    "handshake": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
    "hooks": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80",
    "keyword": "https://images.unsplash.com/photo-1562577309-4932fdd64cd1?w=800&q=80",
    "landscape": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
    "learning": "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&q=80",
    "logo": "https://images.unsplash.com/photo-1559827291-f0049f45f36b?w=800&q=80",
    "marketing": "https://images.unsplash.com/photo-1533750349088-cd871a92f312?w=800&q=80",
    "ml": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&q=80",
    "network": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80",
    "photo": "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800&q=80",
    "prototype": "https://images.unsplash.com/photo-1559028012-481c04fa702d?w=800&q=80",
    "python": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80",
    "react": "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80",
    "seo": "https://images.unsplash.com/photo-1562577309-4932fdd64cd1?w=800&q=80",
    "startup": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&q=80",
    "strategy": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
    "team": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
    "testing": "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=800&q=80",
    "typography": "https://images.unsplash.com/photo-1560732488-6b0df240254a?w=800&q=80",
    "web": "https://images.unsplash.com/photo-1555099962-4199c345e5dd?w=800&q=80",
}

FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=800&q=80",
    "https://images.unsplash.com/photo-1515879218367-8466d910y1984?w=800&q=80",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
    "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&q=80",
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&q=80",
    "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
    "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80",
]

PDF_LESSONS = {
    "Variables and Data Types",
    "Functions & Scope",
    "Component Architecture",
    "Models & Serializers",
    "Figma Interface Tour",
    "Model Evaluation",
    "Feature Engineering",
    "Text Processing",
    "SWOT Analysis",
    "Business Model Canvas",
    "Understanding Exposure",
    "Exporting for Web & Print",
    "Pandas DataFrames",
    "Matplotlib Basics",
    "Keyword Research",
    "Technical SEO Audit",
    "React.memo & useMemo",
    "Bundle Analysis",
    "Typography System",
    "Brand Guidelines Structure",
    "Cap Table Basics",
    "Term Sheet Negotiation",
    "Gear for Landscapes",
    "RAW Processing Workflow",
}


def _image_url(title):
    import hashlib
    title_lower = title.lower()
    for keyword, url in IMAGE_MAP.items():
        if keyword in title_lower:
            return url
    idx = int(hashlib.md5(title.encode()).hexdigest(), 16) % len(FALLBACK_IMAGES)
    return FALLBACK_IMAGES[idx]


def _python_content(title, module, img):
    t = title.lower()
    if "introduction" in t or "intro" in t:
        return f"""![Python]({img})

## What is Python?

Python is a **high-level, interpreted programming language** created by Guido van Rossum and first released in 1991. Its design philosophy emphasizes code readability through significant indentation.

## Key Features

| Feature | Benefit |
|---------|---------|
| Dynamic typing | No type declarations needed |
| Interpreted | Run code immediately without compilation |
| Multi-paradigm | Supports OOP, functional, and procedural styles |
| Extensive standard library | "Batteries included" philosophy |

## Getting Started

Install Python from [python.org](https://python.org), then verify:

```python
python --version
```

Your first program:

```python
print("Hello, World!")
```

## Why Learn Python?

- **Beginner-friendly** — simple syntax that reads like English
- **Highly versatile** — web development, data science, AI, automation
- **Massive ecosystem** — over 400,000 packages on PyPI
- **Strong community** — millions of developers worldwide

## The Python Philosophy

PEP 20 (The Zen of Python) includes guiding principles like "Simple is better than complex" and "Readability counts." These principles shape the language's design and encourage developers to write clean, maintainable code.

Python powers some of the world's largest platforms including Instagram, YouTube, Dropbox, and Spotify, making it one of the most impactful languages ever created.
"""
    elif "variable" in t or "data type" in t:
        return f"""![Data Types]({img})

## Variables in Python

Variables are **named references to objects in memory**. Python uses **dynamic typing** — the interpreter infers the type at runtime.

## Basic Data Types

```python
# Strings
name = "Alice"
greeting = 'Hello'

# Numbers
count = 42          # int
pi = 3.14159        # float
complex_num = 3 + 4j  # complex

# Booleans
is_valid = True
is_done = False

# None
result = None
```

## Collection Types

| Type | Mutable | Ordered | Duplicates | Example |
|------|---------|---------|------------|---------|
| `list` | Yes | Yes | Yes | `[1, 2, 3]` |
| `tuple` | No | Yes | Yes | `(1, 2, 3)` |
| `dict` | Yes | Yes (3.7+) | Keys: No | `{{"a": 1}}` |
| `set` | Yes | No | No | `{{1, 2, 3}}` |

## Type Conversion

Convert between types explicitly using built-in functions:

```python
age = int("25")       # String to integer
text = str(100)       # Integer to string
price = float("19.99")  # String to float
flag = bool(1)        # Integer to boolean (True)
```

Understanding Python's data types is fundamental to writing correct and efficient code. Each type has specific behaviors for memory usage, performance, and available operations.
"""
    elif "control flow" in t:
        return f"""![Control Flow]({img})

## Conditional Statements

Control flow determines **which code executes based on conditions**. Python's `if/elif/else` lets you branch logic cleanly:

```python
age = 18

if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
elif age < 65:
    print("Adult")
else:
    print("Senior")

# Ternary expression
status = "Adult" if age >= 18 else "Minor"
```

## Loops

Python provides two primary loop constructs:

**For loops** iterate over any iterable:

```python
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

for index, item in enumerate(["a", "b", "c"]):
    print(f"{{index}}: {{item}}")
```

**While loops** execute while a condition is True:

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

## Break, Continue, and Else

- `break` — exit the loop immediately
- `continue` — skip to the next iteration
- `for...else` — the `else` block runs if no `break` occurred

## Truthiness

Python treats certain values as falsy: `False`, `None`, `0`, `""`, `[]`, `{{}}`, `()`, `set()`. All other values are truthy. This enables concise checks like `if not items:` to test for empty collections.
"""
    elif "function" in t or "scope" in t:
        return f"""![Functions]({img})

## Defining Functions

Functions are **reusable blocks of code** that perform a specific task. Use the `def` keyword:

```python
def greet(name, greeting="Hello"):
    \"\"\"Return a personalized greeting.\"\"\"
    return f"{{greeting}}, {{name}}!"

message = greet("Alice")
print(message)  # Hello, Alice!

# Keyword arguments
message = greet(name="Bob", greeting="Hi")
```

## Parameters and Arguments

| Type | Example | Description |
|------|---------|-------------|
| Positional | `def add(a, b)` | Matched by order |
| Default | `def power(base, exp=2)` | Optional with fallback |
| Keyword | `func(a=1, b=2)` | Passed by name |
| Variable | `def total(*args)` | Arbitrary positional args |

## Variable Scope (LEGB Rule)

Python resolves names in this order:

1. **L**ocal — inside the current function
2. **E**nclosing — outer functions (nested functions)
3. **G**lobal — the top-level module
4. **B**uilt-in — Python's built-in names

## Lambda Functions

One-line anonymous functions for simple operations:

```python
square = lambda x: x ** 2
numbers = [1, 2, 3, 4]
doubled = list(map(lambda x: x * 2, numbers))
```

Understanding scope is crucial for avoiding bugs with variable shadowing and closures.
"""
    elif "class" in t or "object" in t:
        return f"""![OOP]({img})

## Classes and Objects

Object-Oriented Programming (OOP) models real-world entities as **objects** with **attributes** and **methods**. A **class** is the blueprint; an **object** is an instance.

```python
class Student:
    school = "Python Academy"

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"Hi, I'm {{self.name}}"

alice = Student("Alice", 20)
print(alice.introduce())
```

## Key OOP Concepts

### Encapsulation
Bundle data and methods together. Use underscore prefixes to indicate protected (`_attr`) or private (`__attr`) attributes.

### Instance vs Class Attributes

```python
class Circle:
    pi = 3.14159  # Shared by all instances

    def __init__(self, radius):
        self.radius = radius  # Unique per instance

    def area(self):
        return Circle.pi * self.radius ** 2
```

### Special (Dunder) Methods

```python
class Vector:
    def __init__(self, x, y): ...
    def __add__(self, other): ...
    def __repr__(self): ...
```

These methods let your objects work with Python's built-in operators and functions.
"""
    elif "inheritance" in t:
        return f"""![Inheritance]({img})

## Inheritance in Python

Inheritance lets a **child class** reuse and extend the behaviour of a **parent class**, promoting code reuse and establishing hierarchy.

## Basic Inheritance

```python
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        raise NotImplementedError

class Dog(Animal):
    def speak(self):
        return f"{{self.name}} says Woof!"

class Cat(Animal):
    def speak(self):
        return f"{{self.name}} says Meow!"
```

## The `super()` Function

```python
class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

class Car(Vehicle):
    def __init__(self, brand, model, doors):
        super().__init__(brand, model)
        self.doors = doors
```

## Method Resolution Order (MRO)

Python uses **C3 Linearization** for method lookup. Check with `ClassName.__mro__`:

```python
class A: pass
class B(A): pass
class C(A): pass
class D(B, C): pass
print(D.__mro__)
# D -> B -> C -> A -> object
```

## Types of Inheritance

- **Single** — one parent, one child
- **Multiple** — child inherits from multiple parents
- **Multilevel** — A -> B -> C chain
- **Hierarchical** — one parent, many children

Use inheritance for "is-a" relationships. Prefer composition for "has-a" relationships.
"""
    elif "polymorphism" in t:
        return f"""![Polymorphism]({img})

## Polymorphism in Python

Polymorphism means "many forms" — different classes can be used interchangeably when they share a common interface. Python achieves this through **duck typing**.

## Duck Typing

```python
class Duck:
    def quack(self): return "Quack!"
    def swim(self): return "Swimming"

class Person:
    def quack(self): return "Pretending to be a duck!"
    def swim(self): return "Swimming like a person"

def make_it_quack(entity):
    print(entity.quack())

make_it_quack(Duck())    # Quack!
make_it_quack(Person())  # Pretending to be a duck!
```

## Method Overriding

```python
class Shape:
    def area(self): return 0

class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h
    def area(self): return self.w * self.h

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2

shapes = [Rectangle(5, 10), Circle(7)]
for s in shapes:
    print(s.area())  # 50, 153.93791
```

## Abstract Base Classes

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount): pass

class StripeProcessor(PaymentProcessor):
    def process_payment(self, amount):
        return f"Processing ${{amount}} via Stripe"
```

Polymorphism makes your code flexible and extensible.
"""
    elif "decorator" in t:
        return f"""![Decorators]({img})

## Decorators in Python

Decorators are **functions that modify other functions** — adding behaviour without changing the source code. The `@` syntax is syntactic sugar for `func = decorator(func)`.

## Function Decorators

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{{func.__name__}} took {{elapsed:.4f}}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.5)
    return "Done!"
```

## Decorators with Arguments

```python
def repeat(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {{name}}!")
```

## Practical Use Cases

| Use Case | Description |
|----------|-------------|
| Logging | Record function calls and parameters |
| Authentication | Check permissions before execution |
| Caching | Memoize expensive function results |
| Validation | Check input types and values |

## Built-in Decorators

- `@staticmethod` — method that doesn't access instance/class
- `@classmethod` — method that receives the class
- `@property` — method that behaves like an attribute

Decorators are a powerful metaprogramming tool that enable clean separation of concerns.
"""
    elif "web scraper" in t or "scraping" in t:
        return f"""![Web Scraping]({img})

## Web Scraping with Python

Web scraping is the automated process of **extracting data from websites**. Python's `requests` and `BeautifulSoup` libraries make this accessible.

## Setting Up

```python
import requests
from bs4 import BeautifulSoup

response = requests.get("https://example.com")
soup = BeautifulSoup(response.content, "html.parser")
print(soup.title.text)
```

## Parsing HTML

| Method | Example | Returns |
|--------|---------|---------|
| `find()` | `soup.find("div", class_="content")` | First match |
| `find_all()` | `soup.find_all("a")` | All matches |
| `select()` | `soup.select("div.content a")` | CSS selector matches |

## Building a Real Scraper

```python
import requests
from bs4 import BeautifulSoup
import time

def scrape_quotes():
    quotes = []
    for page in range(1, 11):
        url = f"http://quotes.toscrape.com/page/{{page}}/"
        response = requests.get(url, headers={{"User-Agent": "Mozilla/5.0"}})
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.content, "html.parser")
        for quote in soup.select("div.quote"):
            text = quote.select_one("span.text").text
            author = quote.select_one("small.author").text
            quotes.append({{"text": text, "author": author}})
        time.sleep(1)
    return quotes
```

## Ethical Scraping Checklist

1. **Check `robots.txt`** — respects site rules
2. **Add polite delays** — `time.sleep(1)` between requests
3. **Identify yourself** — set a descriptive User-Agent
4. **Respect rate limits** — don't overwhelm the server
5. **Check ToS** — some sites prohibit scraping

Always scrape ethically and legally.
"""
    elif "cli tool" in t or "cli" in t:
        return f"""![CLI Tool]({img})

## Building CLI Tools in Python

Command-line interface (CLI) tools are **scripts run from the terminal**. Python's `argparse` module makes building professional CLI tools straightforward.

## Using argparse

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Process files.")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--limit", type=int, default=10, help="Items to process")
    args = parser.parse_args()

    if args.verbose:
        print(f"Processing {{args.input}}...")
    with open(args.input) as f:
        data = f.readlines()[:args.limit]
    output = args.output or f"processed_{{args.input}}"
    with open(output, "w") as f:
        f.writelines(data)
    print(f"Wrote {{len(data)}} lines to {{output}}")

if __name__ == "__main__":
    main()
```

## Exit Codes

```python
import sys

if error_occurred:
    print("Error: something went wrong", file=sys.stderr)
    sys.exit(1)
```

## CLI Project Structure

```
my-cli-tool/
├── cli.py        # Entry point
├── commands/     # Subcommands
│   ├── init.py
│   └── deploy.py
├── utils/        # Shared utilities
│   └── helpers.py
└── setup.py      # Package config
```

CLI tools are essential for automation, data processing, and developer workflows.
"""
    elif "file automation" in t or "automation" in t:
        return f"""![File Automation]({img})

## File Automation with Python

Python's `pathlib` and `shutil` modules let you **automate file operations** — rename, move, copy, delete, and organize files programmatically.

## Working with Paths

```python
from pathlib import Path

home = Path.home()
downloads = home / "Downloads"

for file in downloads.iterdir():
    if file.is_file():
        print(file.name, file.suffix)

print(downloads.exists())
print(downloads.stat().st_size)
```

## File Operations

| Operation | Code |
|-----------|------|
| Copy | `shutil.copy2("src.txt", "dst.txt")` |
| Move/Rename | `Path("old.txt").rename("new.txt")` |
| Delete file | `Path("temp.txt").unlink()` |
| Create dirs | `Path("a/b/c").mkdir(parents=True)` |
| Delete tree | `shutil.rmtree("dir")` |

## File Organizer Script

```python
from pathlib import Path
import shutil

CATEGORIES = {{
    "Images": [".jpg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Code": [".py", ".js", ".html", ".css"],
    "Archives": [".zip", ".tar", ".gz"],
}}

def organize(download_path):
    for file in Path(download_path).iterdir():
        if not file.is_file():
            continue
        for category, exts in CATEGORIES.items():
            if file.suffix.lower() in exts:
                target = Path(download_path) / category
                target.mkdir(exist_ok=True)
                shutil.move(str(file), str(target / file.name))
                break
```

File automation is one of the most practical applications of Python for everyday tasks.
"""
    elif "api integration" in t or "api" in t:
        return f"""![API Integration]({img})

## API Integration with Python

REST APIs allow different software systems to **communicate over HTTP**. Modern applications integrate multiple APIs.

## REST API Fundamentals

```python
import requests

# GET request
response = requests.get("https://api.github.com/users/python")
user = response.json()
print(user["login"], user["public_repos"])

# POST request
new = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={{"title": "Hello", "body": "World", "userId": 1}}
)
print(new.status_code)  # 201
```

## Authentication Methods

| Method | Header |
|--------|--------|
| API Key | `{{"X-API-Key": "your-key"}}` |
| Bearer Token | `{{"Authorization": "Bearer <token>"}}` |
| Basic Auth | `requests.get(url, auth=(user, pass))` |

## Error Handling

```python
def safe_call(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {{"error": "Timeout"}}
    except requests.exceptions.ConnectionError:
        return {{"error": "Connection failed"}}
    except requests.exceptions.HTTPError as e:
        return {{"error": f"HTTP {{e.response.status_code}}"}}
```

## Best Practices

- Handle rate limiting (HTTP 429) with retry logic
- Use environment variables for API keys
- Implement proper timeout values
- Cache responses when appropriate

API integration skills are essential for building modern connected applications.
"""
    return ""


def _fullstack_content(title, module, img):
    t = title.lower()
    if "component" in t and "architect" in t:
        return f"""![Components]({img})

## Component Architecture

React applications are built from **components** -- independent, reusable pieces of UI.

## Functional Components

```jsx
function Welcome({{ name }}) {{
  return <h1>Hello, {{name}}!</h1>;
}}

<Welcome name="Alice" />
```

## Component Design Principles

| Principle | Description |
|-----------|-------------|
| Single Responsibility | Each component does one thing |
| Composition over Inheritance | Combine rather than extend |
| Props down, events up | Unidirectional data flow |

## Props and Data Flow

Data flows **down** the component tree via props. Events flow **up** through callbacks.
"""
    elif "state" in t or "props" in t:
        return f"""![State & Props]({img})

## State and Props in React

**Props** are immutable data passed from parent to child. **State** is mutable data managed within a component.

## Props

```jsx
function Greeting({{ name, age }}) {{
  return <h1>Hello, {{name}}! You are {{age}}.</h1>;
}}

<Greeting name="Alice" age={{25}} />
```

## State with useState

```jsx
function Counter() {{
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>Count: {{count}}</p>
      <button onClick={{() => setCount(count + 1)}}>+</button>
    </div>
  );
}}
```

## State vs Props

| Aspect | Props | State |
|--------|-------|-------|
| Mutability | Immutable | Mutable |
| Owner | Parent | Component itself |
| Purpose | Configuration | Dynamic data |

## Rules of Hooks

1. Only call hooks at the **top level**
2. Only call hooks from **React function components**
3. Don't call hooks inside conditions, loops, or nested functions
"""
    elif "hooks deep" in t or "hooks" in t:
        return f"""![Hooks]({img})

## React Hooks Deep Dive

Hooks let you **use state and lifecycle features in functional components**.

## Core Hooks

```jsx
useEffect(() => {{
  document.title = `Count: ${{count}}`;
  return () => {{ /* cleanup */ }};
}}, [count]);
```

## useEffect Lifecycle

| Dependency Array | Runs On |
|-----------------|---------|
| Not provided | Every render |
| `[]` | Mount only |
| `[a, b]` | When a or b changes |

## useRef

```jsx
const inputRef = useRef(null);

function focusInput() {{
  inputRef.current.focus();
}}

return <input ref={{inputRef}} />;
```

## Custom Hooks

Extract and reuse stateful logic:

```jsx
function useLocalStorage(key, initialValue) {{
  const [value, setValue] = useState(() => {{
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : initialValue;
  }});

  useEffect(() => {{
    localStorage.setItem(key, JSON.stringify(value));
  }}, [key, value]);

  return [value, setValue];
}}
```

Hooks enable powerful patterns and eliminate the need for class components.
"""
    elif "context api" in t or ("context" in t and "content" not in t and "at scale" not in t):
        return f"""![Context API]({img})

## Context API in React

The Context API provides a way to **share data across the component tree** without prop drilling.

## Creating Context

```jsx
import {{ createContext, useContext }} from "react";

const ThemeContext = createContext("light");

function App() {{
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}}
```

## Consuming Context

```jsx
function ThemedButton() {{
  const theme = useContext(ThemeContext);
  return <button className={{theme}}>Click me</button>;
}}
```

## When to Use Context

| Use Context When | Don't Use Context When |
|-----------------|----------------------|
| Theme/settings | Simple prop drilling (1-2 levels) |
| Auth/user data | Component-specific state |
| Locale/i18n | Frequent updates |

## Performance

Context re-renders all consumers when its value changes. Split contexts by domain, use useMemo to stabilize values.
"""
    elif "model" in t or "serializer" in t:
        return f"""![Django Models]({img})

## Models and Serializers

**Models** define your data structure. **Serializers** convert complex data to JSON and validate input.

## Defining Models

```python
from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

## Creating Serializers

```python
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "description", "created_at"]
        read_only_fields = ["id", "created_at"]
```

## Field Types

| Model Field | Serializer Field | DB Column |
|-------------|-----------------|-----------|
| CharField | CharField | VARCHAR |
| IntegerField | IntegerField | INTEGER |
| ForeignKey | PrimaryKeyRelatedField | INTEGER (FK) |

Models and serializers form the backbone of any DRF API.
"""
    elif "api view" in t:
        return f"""![API Views]({img})

## API Views in DRF

API views handle HTTP requests and return responses.

## Function-Based Views

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET", "POST"])
def product_list(request):
    if request.method == "GET":
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

## Class-Based Views

```python
from rest_framework import generics

class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
```

## ViewSets

```python
from rest_framework import viewsets

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register("products", ProductViewSet)
```

| View | Methods | URL |
|------|---------|-----|
| ListCreateAPIView | GET, POST | `/products/` |
| RetrieveUpdateDestroyAPIView | GET, PUT, PATCH, DELETE | `/products/{{id}}/` |
"""
    elif "authentication" in t:
        return f"""![Auth]({img})

## Authentication in DRF

Authentication identifies **who is making the request**.

## Token Authentication

```python
REST_FRAMEWORK = {{
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ]
}}
```

## JWT Authentication

```python
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
]
```

## Protecting Views

```python
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
```

## Authentication vs Permissions

- **Authentication** -- who are you?
- **Permissions** -- what are you allowed to do?
"""
    elif "permission" in t:
        return f"""![Permissions]({img})

## Permissions in DRF

Permissions determine **what an authenticated user is allowed to do**.

## Object-Level Permissions

```python
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

## Common Patterns

| Requirement | Approach |
|-------------|----------|
| Need login | `IsAuthenticated` |
| Admin only | `IsAdminUser` |
| Own data only | Custom `IsOwner` |
| Role-based | Django Groups + custom permission |
"""
    elif "connecting" in t or ("frontend" in t and "backend" in t):
        return f"""![Full Stack]({img})

## Connecting Frontend and Backend

A full-stack app requires seamless communication between **React** and **Django** via REST APIs.

## API Client Setup

```javascript
import axios from "axios";

const api = axios.create({{
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000/api",
}});

api.interceptors.request.use((config) => {{
  const token = localStorage.getItem("access_token");
  if (token) {{
    config.headers.Authorization = `Bearer ${{token}}`;
  }}
  return config;
}});
```

## CORS Configuration

```python
INSTALLED_APPS = ["corsheaders"]
MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"]
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
```

## Data Fetching

```jsx
function ProductList() {{
  const [products, setProducts] = useState([]);

  useEffect(() => {{
    api.get("/products/").then((r) => setProducts(r.data));
  }}, []);

  return products.map((p) => <div key={{p.id}}>{{p.name}}</div>);
}}
```

## Deployment Checklist

| Item | Description |
|------|-------------|
| API URL | Set via environment variable |
| CORS | Configure for production domain |
| Static files | Serve from Django or CDN |
| HTTPS | Enable in production |
"""
    elif "docker" in t and ("setup" in t or "deployment" in t):
        return f"""![Docker]({img})

## Docker Setup

Docker **containerizes applications** so they run consistently everywhere.

## Docker Compose

```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
```

## Dockerfile for Django

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## Dockerfile for React

```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
```

Containerization ensures consistency across all environments.
"""
    elif "aws" in t or "deployment" in t:
        return f"""![AWS]({img})

## AWS Deployment

Amazon Web Services provides a comprehensive cloud platform for deploying web applications.

## Architecture

User -> CloudFront -> ALB -> ECS (Django + React) -> RDS (PostgreSQL)
  -> S3 (Static files)

## Key Services

| Service | Purpose |
|---------|---------|
| EC2 / ECS | Compute (running containers) |
| RDS | Managed database |
| S3 | File storage |
| CloudFront | CDN |
| Route 53 | DNS management |

## Deployment Steps

1. Build and tag Docker images
2. Push to ECR
3. Create ECS task definition
4. Set up RDS
5. Configure ALB with HTTPS
6. Deploy with ECS service (blue/green)
"""
    elif "ci/cd" in t or "ci" in t:
        return f"""![CI/CD]({img})

## CI/CD Pipeline

Continuous Integration and Continuous Deployment **automates build, test, and deployment**.

## GitHub Actions

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pip install -r requirements.txt && pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: aws ecs update-service --cluster prod --service myapp --force-new-deployment
```

## Pipeline Stages

| Stage | Purpose |
|-------|---------|
| Lint | Code quality |
| Test | Verify correctness |
| Build | Create artifacts |
| Deploy | Release to environment |
| Monitor | Track performance |

## Best Practices

1. **Fail fast** -- run the fastest checks first
2. **Immutable artifacts** -- build once, deploy everywhere
3. **Rollback strategy** -- know how to revert
"""
    return ""


def _advanced_react_content(title, module, img):
    t = title.lower()
    if "compound" in t:
        return f"""![Compound Components]({img})

## Compound Components

Compound components enable a **flexible, declarative API** where a parent manages state implicitly.

```jsx
const Tabs = ({{ children }}) => {{
  const [active, setActive] = useState(0);
  return (
    <TabsContext.Provider value={{{{ active, setActive }}}}>
      {{children}}
    </TabsContext.Provider>
  );
}};

Tabs.Tab = ({{ index, children }}) => {{
  const {{ active, setActive }} = useContext(TabsContext);
  return (
    <button className={{active === index ? "active" : ""}}
            onClick={{() => setActive(index)}}>
      {{children}}
    </button>
  );
}};
```

| Benefit | Description |
|---------|-------------|
| Expressive API | Feels like native HTML |
| Implicit state | Context handles sharing internally |
| Flexible layout | Consumer controls structure |

Used by Reach UI, Chakra UI, and Headless UI.
"""
    elif "render prop" in t:
        return f"""![Render Props]({img})

## Render Props Pattern

A **function as a prop** controls what gets rendered, enabling logic sharing without dictating UI.

```jsx
const MouseTracker = ({{ render }}) => {{
  const [position, setPosition] = useState({{ x: 0, y: 0 }});

  useEffect(() => {{
    const handler = (e) => setPosition({{ x: e.clientX, y: e.clientY }});
    window.addEventListener("mousemove", handler);
    return () => window.removeEventListener("mousemove", handler);
  }}, []);

  return render(position);
}};

<MouseTracker
  render={{({{ x, y }}) => (
    <h1>Mouse: {{x}}, {{y}}</h1>
  )}}
/>
```

Modern React often uses custom hooks instead, but render props remain valuable in specific scenarios.
"""
    elif "custom hook" in t:
        return f"""![Custom Hooks]({img})

## Custom Hooks

Custom hooks **extract and reuse stateful logic** across components.

```jsx
function useLocalStorage(key, initialValue) {{
  const [value, setValue] = useState(() => {{
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : initialValue;
  }});

  useEffect(() => {{
    localStorage.setItem(key, JSON.stringify(value));
  }}, [key, value]);

  return [value, setValue];
}}

const [theme, setTheme] = useLocalStorage("theme", "light");
```

## Rules for Custom Hooks

| Rule | Why |
|------|-----|
| Start with `use` | Enables linting |
| Call at top level | Maintains call order |
| Don't call in conditions | Must be consistent per render |
"""
    elif "higher-order" in t or "hoc" in t:
        return f"""![HOC]({img})

## Higher-Order Components

A function that **takes a component and returns a new component with added functionality**.

```jsx
const withLogging = (WrappedComponent) => {{
  return (props) => {{
    useEffect(() => {{
      console.log(`Rendering ${{WrappedComponent.name}}`);
    }});
    return <WrappedComponent {{...props}} />;
  }};
}};

const withAuth = (WrappedComponent) => {{
  return (props) => {{
    const {{ user }} = useAuth();
    if (!user) return <Navigate to="/login" />;
    return <WrappedComponent {{...props}} user={{user}} />;
  }};
}};
```

## HOCs vs Hooks

| HOC | Hook |
|-----|------|
| Wraps component | Called inside component |
| Adds nesting in DevTools | Flat component tree |
| Harder TypeScript support | Better TypeScript support |
"""
    elif "memo" in t or "usememo" in t:
        return f"""![React Memo]({img})

## React.memo and useMemo

**Memoization** caches computed values so they are only recalculated when dependencies change.

## React.memo

```jsx
const ExpensiveComponent = React.memo(({{ data }}) => {{
  return <div>{{/* Complex rendering */}}</div>;
}});
```

## useMemo

```jsx
const sortedList = useMemo(() => {{
  return [...items].sort((a, b) => a.name.localeCompare(b.name));
}}, [items]);
```

## useCallback

```jsx
const handleClick = useCallback(() => {{
  doSomething(id);
}}, [id]);
```

## When to Memoize

| Scenario | Memoize? |
|----------|----------|
| Expensive computation | Yes |
| Stable prop reference | Yes |
| Simple calculation | No |
| Infrequent updates | No |

Always **profile first** using React DevTools Profiler.
"""
    elif "code splitting" in t:
        return f"""![Code Splitting]({img})

## Code Splitting

Code splitting **divides your bundle into chunks** loaded on demand, reducing initial load time.

## React.lazy and Suspense

```jsx
import {{ lazy, Suspense }} from "react";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));

function App() {{
  return (
    <Suspense fallback={{<div>Loading...</div>}}>
      <Routes>
        <Route path="/dashboard" element={{<Dashboard />}} />
        <Route path="/settings" element={{<Settings />}} />
      </Routes>
    </Suspense>
  );
}}
```

## Benefits

| Benefit | Practice |
|---------|----------|
| Faster initial load | Split by routes |
| Reduced bundle size | Avoid splitting tiny modules |
| Better caching | Content hashes in chunk names |
"""
    elif "virtualization" in t or "virtual" in t:
        return f"""![Virtualization]({img})

## Virtualization

Virtualization **renders only visible items** in a large list, dramatically improving performance.

```jsx
import {{ FixedSizeList }} from "react-window";

const Row = ({{ index, style }}) => (
  <div style={{style}}>Item {{index + 1}}</div>
);

function VirtualList({{ items }}) {{
  return (
    <FixedSizeList
      height={{400}}
      itemCount={{items.length}}
      itemSize={{50}}
      width={{300}}
    >
      {{Row}}
    </FixedSizeList>
  );
}}
```

## Performance

| Items | Without | With |
|-------|---------|------|
| 1,000 | 50ms render | 5ms render |
| 10,000 | 500ms render | 5ms render |
| 100,000 | Crash | 5ms render |
"""
    elif "bundle analysis" in t or "bundle" in t:
        return f"""![Bundle Analysis]({img})

## Bundle Analysis

Analyzing your bundle helps **identify large dependencies and optimization opportunities**.

## Tools

| Tool | Purpose |
|------|---------|
| Webpack Bundle Analyzer | Interactive treemap |
| Source Map Explorer | Analyze with source maps |
| BundlePhobia | Check package size before installing |

## Strategies

1. Tree shaking -- remove unused exports
2. Code splitting -- route-based chunks
3. Image optimization -- WebP, lazy loading

Optimization targets: moment.js (278KB) -> date-fns (22KB), lodash (540KB) -> lodash-es (70KB)
"""
    elif "context at scale" in t or ("context" in t and "api" not in t):
        return f"""![Context at Scale]({img})

## Context at Scale

As apps grow, naive Context usage causes **excessive re-renders**.

## The Problem

```jsx
const AppContext = createContext();

function App() {{
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState("light");

  return (
    <AppContext.Provider value={{{{ user, theme, setUser, setTheme }}}}>
      <Dashboard />
    </AppContext.Provider>
  );
}}
```

## Solutions

### Split Contexts

```jsx
<UserContext.Provider value={{{{ user, setUser }}}}>
  <ThemeContext.Provider value={{{{ theme, setTheme }}}}>
    <Dashboard />
  </ThemeContext.Provider>
</UserContext.Provider>
```

### UseMemo

```jsx
const value = useMemo(() => ({{{{ user, setUser }}}}), [user]);
```

### Use External Libraries

For high-frequency updates, consider Zustand or React Query.
"""
    elif "zustand" in t:
        return f"""![Zustand]({img})

## Zustand State Management

Zustand is a **minimal, fast state management library** -- no providers, no boilerplate.

## Basic Store

```jsx
import {{ create }} from "zustand";

const useStore = create((set) => ({{
  count: 0,
  increment: () => set((state) => ({{ count: state.count + 1 }})),
  decrement: () => set((state) => ({{ count: state.count - 1 }})),
}}));

function Counter() {{
  const {{ count, increment, decrement }} = useStore();
  return (
    <div>
      <button onClick={{decrement}}>-</button>
      <span>{{count}}</span>
      <button onClick={{increment}}>+</button>
    </div>
  );
}}
```

## Selectors

```jsx
const count = useStore((state) => state.count);
```

## Zustand vs Redux

| Aspect | Zustand | Redux |
|--------|---------|-------|
| Bundle size | ~1KB | ~12KB |
| Provider needed | No | Yes |
| Learning curve | Low | Medium |
"""
    elif "react query" in t or "tanstack" in t:
        return f"""![React Query]({img})

## React Query (TanStack Query)

React Query is a **server-state management library** handling caching, background refetching, and optimistic updates.

## Basic Query

```jsx
import {{ useQuery }} from "@tanstack/react-query";

function ProductList() {{
  const {{ data, isLoading }} = useQuery({{
    queryKey: ["products"],
    queryFn: () => api.get("/products/").then((r) => r.data),
  }});

  if (isLoading) return <Spinner />;
  return data.map((p) => <ProductCard key={{p.id}} product={{p}} />);
}}
```

## Mutations

```jsx
const {{ mutate }} = useMutation({{
  mutationFn: (newProduct) => api.post("/products/", newProduct),
  onSuccess: () => {{
    queryClient.invalidateQueries({{ queryKey: ["products"] }});
  }},
}});
```

React Query eliminates manual API state management, reducing boilerplate by up to 50%.
"""
    elif "optimistic" in t:
        return f"""![Optimistic Updates]({img})

## Optimistic Updates

Optimistic updates **update the UI immediately** before server confirmation, then revert on error.

```jsx
const {{ mutate }} = useMutation({{
  mutationFn: (updatedTodo) =>
    api.patch(`/todos/${{updatedTodo.id}}`, updatedTodo),

  onMutate: async (updatedTodo) => {{
    await queryClient.cancelQueries({{ queryKey: ["todos"] }});
    const previous = queryClient.getQueryData(["todos"]);

    queryClient.setQueryData(["todos"], (old) =>
      old.map((t) => (t.id === updatedTodo.id ? updatedTodo : t))
    );

    return {{ previous }};
  }},

  onError: (err, updatedTodo, context) => {{
    queryClient.setQueryData(["todos"], context.previous);
  }},

  onSettled: () => {{
    queryClient.invalidateQueries({{ queryKey: ["todos"] }});
  }},
}});
```

Best for actions that almost always succeed, like toggling a todo or liking a post.
"""
    return ""


def _design_content(title, module, img):
    t = title.lower()
    if "empathize" in t or "empathy" in t:
        return f"""![Empathize]({img})

## The Empathize Phase

The first stage of Design Thinking -- **understanding users' needs, behaviours, and motivations**.

## Why Empathize Matters

- **Uncover latent needs** users cannot articulate directly
- **Challenge assumptions** about user behaviour
- **Build emotional resonance** into your designs

## Empathy Methods

| Method | Description |
|--------|-------------|
| User Interviews | One-on-one conversations |
| Contextual Inquiry | Observe users in their environment |
| Surveys | Quantitative data collection |
| Diary Studies | Users log experiences over time |
| Empathy Mapping | Synthesize observations |

## Conducting Interviews

1. Prepare -- define goals, write discussion guide
2. Recruit -- find representative users
3. Interview -- ask open-ended questions, listen more
4. Synthesize -- identify patterns and insights
5. Share -- communicate findings to stakeholders

The goal is not to validate your ideas but to understand your users deeply.
"""
    elif "define" in t or "ideate" in t:
        return f"""![Define & Ideate]({img})

## Define and Ideate Phases

The **Define phase** synthesizes findings into a clear problem statement. The **Ideate phase** generates potential solutions.

## Problem Statement Format

[User] needs [need] because [insight].

Example: "Busy professionals need a way to track daily water intake because they often forget to hydrate during work hours."

## Ideation Techniques

| Technique | Description |
|-----------|-------------|
| Brainstorming | Free-form idea generation |
| SCAMPER | Substitute, Combine, Adapt, Modify, Eliminate, Reverse |
| Crazy 8s | 8 ideas in 8 minutes |
| Mind Mapping | Visual idea exploration |

## Ideation Rules

1. Defer judgment -- no idea is too crazy
2. Build on others -- "Yes, and..."
3. Go for quantity -- 100 ideas > 10
4. Stay focused -- keep the problem statement visible
"""
    elif "prototyping" in t:
        return f"""![Prototyping]({img})

## Prototyping Basics

Prototyping creates **low-fidelity representations** to test with users.

## Fidelity Levels

| Fidelity | Tools | Purpose | Time |
|----------|-------|---------|------|
| Low | Paper, whiteboard | Test flow and layout | Minutes |
| Medium | Figma, Sketch | Test interactions | Hours |
| High | Figma prototypes | Test detailed interactions | Days |

## What to Test

| Test This | Not This |
|-----------|----------|
| User flow and navigation | Visual polish |
| Content and copy | Final colours |
| Task completion | Pixel perfection |
"""
    elif "usability" in t or "testing" in t:
        return f"""![Usability Testing]({img})

## Usability Testing

Usability testing **evaluates a product by testing with representative users**.

## Types of Testing

| Type | When | Method |
|------|------|--------|
| Formative | Early design | Paper prototypes |
| Summative | Before launch | High-fidelity prototype |
| Comparative | Feature decisions | A/B testing |

## What to Measure

| Metric | What It Tells You |
|--------|-------------------|
| Task success rate | Can users complete the task? |
| Time on task | How efficient is the flow? |
| Error rate | Where do users get confused? |
| SUS score | Overall usability score |

Test with 5 users per round to catch ~85% of issues.
"""
    elif "figma" in t and ("interface" in t or "tour" in t):
        return f"""![Figma]({img})

## Figma Interface Tour

Figma is a **cloud-based design tool** enabling real-time collaboration.

## Key Panels

| Panel | Purpose |
|-------|---------|
| Layers Panel | View and organize elements |
| Design Panel | Adjust element properties |
| Prototype Panel | Create interactions |
| Assets Panel | Access components and styles |

## Shortcuts

| Shortcut | Action |
|----------|--------|
| `F` | Create frame |
| `R` | Create rectangle |
| `T` | Text tool |
| `Ctrl+D` | Duplicate |

## Collaboration

Multiplayer editing, comments, version history, shared libraries, and developer handoff with inspect mode.
"""
    elif "auto layout" in t:
        return f"""![Auto Layout]({img})

## Auto Layout in Figma

Auto Layout is a **constraint-based layout system** similar to CSS Flexbox.

## Properties

| Property | Description | CSS Equivalent |
|----------|-------------|----------------|
| Direction | Horizontal or vertical | `flex-direction` |
| Spacing | Gap between items | `gap` |
| Padding | Space around content | `padding` |
| Alignment | Items alignment | `align-items` |

## Nesting

```css
.card {{
  display: flex;
  flex-direction: column;
  padding: 16px;
  gap: 8px;
}}

.card-header {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
```

Auto Layout is one of Figma's most powerful features.
"""
    elif "components" in t and "variant" in t:
        return f"""![Components & Variants]({img})

## Components and Variants

Components are **reusable design elements**. Variants group related states into a set.

## Using Variants

```
Button
+-- Default (Button/Default)
+-- Hover (Button/Hover)
+-- Disabled (Button/Disabled)
+-- Focus (Button/Focus)
```

## Properties

| Type | Example | Use Case |
|------|---------|----------|
| Boolean | `Icon: true/false` | Show/hide elements |
| Text | `Label: "Submit"` | Dynamic text |
| Instance swap | `Icon: arrow/check` | Swap instances |
| Variant | `State: default/hover` | Switch modes |

## Best Practices

- Use auto layout for flexible components
- Add descriptions to component properties
- Keep libraries in dedicated files
"""
    elif "interactive" in t and "prototype" in t:
        return f"""![Interactive Prototypes]({img})

## Interactive Prototypes in Figma

Interactive prototypes **bring your designs to life** before development.

## Creating Interactions

1. Go to the **Prototype** tab
2. Select a layer
3. Drag the connector to the destination
4. Configure interaction details

## Interaction Types

| Trigger | Action | Animation |
|---------|--------|-----------|
| On Tap | Navigate to | Instant |
| On Drag | Open overlay | Dissolve |
| While Hovering | Swap with | Smart Animate |

## Smart Animate

Detects matching layers and animates differences. Requires same layer names and consistent structure.

## Best Practices

- Focus on key user flows
- Use realistic content
- Test on actual device dimensions
- Share early and often for feedback
"""
    return ""


def _ml_content(title, module, img):
    t = title.lower()
    if "linear" in t and "regression" in t:
        return f"""![Linear Regression]({img})

## Linear Regression

Models the **relationship between a dependent variable and independent variables** by fitting a linear equation.

## The Model

y = b0 + b1*x1 + b2*x2 + ... + bn*xn + e

## Implementation

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

print(f"R2: {{r2_score(y_test, y_pred):.3f}}")
print(f"MSE: {{mean_squared_error(y_test, y_pred):.3f}}")
```

## Evaluation

| Metric | Formula | Best |
|--------|---------|------|
| R2 | 1 - SSres/SStot | 1 |
| MSE | sum((y-y_pred)^2)/n | 0 |
| RMSE | sqrt(MSE) | 0 |

## Assumptions

1. **Linearity** -- relationship is linear
2. **Independence** -- observations are independent
3. **Homoscedasticity** -- constant error variance
4. **Normality** -- errors are normally distributed
"""
    elif "classification" in t:
        return f"""![Classification]({img})

## Classification Algorithms

Classification predicts **discrete class labels** from input features.

## Common Algorithms

| Algorithm | Type | Best For |
|-----------|------|----------|
| Logistic Regression | Linear | Binary, baseline |
| KNN | Instance-based | Small datasets |
| Decision Trees | Tree-based | Interpretability |
| Random Forest | Ensemble | High accuracy |
| SVM | Margin-based | High-dimensional data |

## Example

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(f"Accuracy: {{accuracy_score(y_test, y_pred):.3f}}")
```

## Evaluation

| Metric | Formula | Use Case |
|--------|---------|----------|
| Accuracy | (TP+TN)/Total | Balanced classes |
| Precision | TP/(TP+FP) | Costly FP |
| Recall | TP/(TP+FN) | Costly FN |
| F1-Score | 2*P*R/(P+R) | Imbalanced classes |
"""
    elif "model evaluation" in t:
        return f"""![Model Evaluation]({img})

## Model Evaluation

Proper evaluation is crucial for understanding **how well your model generalizes**.

## Train/Test Split

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

## Cross-Validation

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
print(f"Mean: {{scores.mean():.3f}} (+/- {{scores.std() * 2:.3f}})")
```

## Bias-Variance Tradeoff

- **Underfitting** (High Bias) -- model too simple
- **Overfitting** (High Variance) -- model too complex

## Common Pitfalls

| Pitfall | Impact | Solution |
|---------|--------|----------|
| Data leakage | Overly optimistic | Proper separation |
| Imbalanced data | Misleading accuracy | Use F1-score |
| Temporal drift | Model degrades | Monitor and retrain |
"""
    elif "feature engineering" in t or "feature" in t:
        return f"""![Feature Engineering]({img})

## Feature Engineering

**Transforming raw data into features** that better represent the underlying problem.

## Handling Missing Values

```python
df["age"].fillna(df["age"].median(), inplace=True)
df["age_missing"] = df["age"].isna().astype(int)
```

## Encoding Categorical Variables

```python
pd.get_dummies(df, columns=["color"])

from sklearn.preprocessing import LabelEncoder
df["category"] = LabelEncoder().fit_transform(df["category"])
```

## Feature Scaling

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler

StandardScaler().fit_transform(X)     # mean=0, std=1
MinMaxScaler().fit_transform(X)        # range [0, 1]
```

## Interaction Features

```python
df["area"] = df["width"] * df["height"]
df["price_per_sqft"] = df["price"] / df["sqft"]
df["age_squared"] = df["age"] ** 2
```

Good feature engineering often matters more than the choice of algorithm.
"""
    elif "neural network" in t or "neural" in t or "network" in t:
        return f"""![Neural Networks]({img})

## Neural Network Basics

**Computing systems inspired by biological neural networks**, consisting of interconnected nodes in layers.

## Implementation with Keras

```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation="relu", input_shape=(10,)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(optimizer="adam", loss="binary_crossentropy",
              metrics=["accuracy"])
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
```

## Activation Functions

| Function | Range | Use Case |
|----------|-------|----------|
| ReLU | [0, inf) | Hidden layers |
| Sigmoid | (0, 1) | Binary classification |
| Softmax | (0, 1) sum=1 | Multi-class |

## Key Hyperparameters

- **Learning rate** -- step size during optimization
- **Batch size** -- samples per gradient update
- **Dropout rate** -- regularization strength
"""
    elif "cnn" in t or "convolutional" in t or "vision" in t:
        return f"""![CNNs]({img})

## CNNs for Vision

Convolutional Neural Networks are **specialized for processing grid-like data** such as images.

## Building a CNN

```python
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, (3,3), activation="relu", input_shape=(224,224,3)),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(64, (3,3), activation="relu"),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Conv2D(128, (3,3), activation="relu"),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation="relu"),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(10, activation="softmax")
])
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| Convolution | Slide filter over input to detect features |
| Pooling | Downsample to reduce dimensions |
| Stride | Step size of convolution |
| Feature maps | Output of convolution operations |

## Transfer Learning

```python
base = tf.keras.applications.ResNet50(weights="imagenet", include_top=False)
base.trainable = False
model = tf.keras.Sequential([base, tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(num_classes, activation="softmax")])
```
"""
    elif "rnn" in t or "lstm" in t or "recurrent" in t:
        return f"""![RNNs & LSTMs]({img})

## RNNs and LSTMs

Recurrent Neural Networks are **designed for sequential data** -- text, time series, audio.

## Implementation

```python
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(vocab_size, 128, input_length=100),
    tf.keras.layers.LSTM(128, return_sequences=True),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(num_classes, activation="softmax")
])
```

## LSTM vs GRU

| Feature | LSTM | GRU |
|---------|------|-----|
| Gates | 3 (forget, input, output) | 2 (reset, update) |
| Parameters | More | Fewer |
| Training | Slower | Faster |

## Applications

- Text generation
- Time series forecasting
- Speech recognition
- Machine translation
"""
    elif "transfer" in t and "learning" in t:
        return f"""![Transfer Learning]({img})

## Transfer Learning

**Leverage knowledge from a pre-trained model** and adapt it to a new task.

## Approaches

| Approach | Freeze | Train | Use Case |
|----------|--------|-------|----------|
| Feature extraction | All base | New classifier | Small dataset |
| Fine-tuning | Early layers | Later + classifier | Medium dataset |
| Full fine-tuning | None | All | Large dataset |

## Feature Extraction

```python
base = tf.keras.applications.ResNet50(weights="imagenet", include_top=False)
base.trainable = False

model = tf.keras.Sequential([
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(num_classes, activation="softmax")
])
```

## Fine-Tuning Strategy

1. Train classifier head with frozen base (few epochs)
2. Unfreeze top layers of the base model
3. Continue training with a lower learning rate (1/10th)

## Popular Models

| Model | Size | Best For |
|-------|------|----------|
| ResNet | 25-200MB | General vision |
| EfficientNet | 5-50MB | Efficiency |
| BERT | 400MB | NLP tasks |
"""
    elif "text processing" in t or "nlp" in t:
        return f"""![Text Processing]({img})

## Text Processing for NLP

**Converts raw text into a format ML models can understand**.

## Pipeline

```python
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\\s]", "", text)
    tokens = nltk.word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [t for t in tokens if t not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)
```

## Text Representation

| Method | Description | Pros |
|--------|-------------|------|
| Bag of Words | Word count vector | Simple |
| TF-IDF | Weighted frequency | Downplays common words |
| Word Embeddings | Dense vectors | Captures semantics |

## TF-IDF

```python
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
X = vectorizer.fit_transform(documents)
```
"""
    elif "transformer" in t or "bert" in t:
        return f"""![Transformers]({img})

## Transformers and BERT

Transformers process **all input tokens simultaneously** using the attention mechanism.

## Using BERT

```python
from transformers import BertTokenizer, BertModel

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

inputs = tokenizer("Transformers are amazing!",
                   return_tensors="pt", padding=True, truncation=True)
outputs = model(**inputs)
embedding = outputs.last_hidden_state[:, 0, :]
```

## Attention

attention_scores = query @ key.T / sqrt(d_k)
attention_weights = softmax(attention_scores)
output = attention_weights @ value

## Key Innovations

| Innovation | Description |
|------------|-------------|
| Self-Attention | Every token attends to every other |
| Multi-Head | Multiple attention mechanisms in parallel |
| Bidirectional | Both left and right context |
"""
    elif "fastapi" in t or "serving" in t:
        return f"""![FastAPI]({img})

## Serving ML Models with FastAPI

FastAPI is a **modern, fast web framework** ideal for serving ML models.

## Basic API

```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="ML Model API")
model = joblib.load("model.pkl")

class PredictionInput(BaseModel):
    features: list[float]

class PredictionOutput(BaseModel):
    prediction: float
    confidence: float

@app.post("/predict", response_model=PredictionOutput)
def predict(input_data: PredictionInput):
    X = np.array(input_data.features).reshape(1, -1)
    pred = model.predict(X)[0]
    proba = model.predict_proba(X).max()
    return PredictionOutput(prediction=pred, confidence=float(proba))
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Single prediction |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |

## Best Practices

- Load model once at startup
- Use batching for efficiency
- Monitor latency and errors
"""
    elif "docker" in t or "sagemaker" in t or "aws" in t:
        return f"""![Docker & SageMaker]({img})

## Docker + AWS SageMaker

SageMaker is a **fully managed ML platform** for the entire ML workflow.

## Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY model.pkl .
COPY app.py .
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

## SageMaker Deployment

```python
import sagemaker
from sagemaker.model import Model

model = Model(
    image_uri="<account>.dkr.ecr.<region>.amazonaws.com/my-model:latest",
    role=sagemaker.get_execution_role(),
)
predictor = model.deploy(
    initial_instance_count=1, instance_type="ml.m5.large"
)
```

## SageMaker vs Self-Managed

| Aspect | SageMaker | Self-Managed |
|--------|-----------|--------------|
| Setup time | Minutes | Hours |
| Auto-scaling | Built-in | Manual |
| Cost | Slightly higher | Lower |
"""
    return ""


def _photography_content(title, module, img):
    t = title.lower()
    if "exposure" in t:
        return f"""![Exposure]({img})

## Understanding Exposure

Exposure is the **amount of light that reaches your camera sensor**. It is controlled by aperture, shutter speed, and ISO.

## The Exposure Triangle

Aperture (Depth of Field) -- Shutter Speed (Motion blur) -- ISO (Noise)

## How They Interact

| Setting | More Light | Less Light | Side Effect |
|---------|------------|------------|-------------|
| Aperture | Lower f-number | Higher f-number | Shallow DOF |
| Shutter Speed | Slower | Faster | Motion blur |
| ISO | Higher | Lower | More noise |

## Metering Modes

| Mode | How It Measures | Best For |
|------|-----------------|----------|
| Evaluative | Entire frame | General use |
| Center-weighted | Center emphasis | Portraits |
| Spot | Small area | High contrast scenes |

Understanding exposure is the foundation of photography.
"""
    elif "aperture" in t or "depth of field" in t:
        return f"""![Aperture]({img})

## Aperture and Depth of Field

Aperture is the **opening in the lens that controls light entry**. It also determines depth of field.

## Aperture Stops

| f-stop | Light | Depth of Field |
|--------|-------|----------------|
| f/1.4 | Maximum | Very shallow |
| f/2.8 | 1/4 of f/1.4 | Shallow |
| f/5.6 | 1/16 of f/1.4 | Moderate |
| f/11 | 1/64 of f/1.4 | Deep |
| f/22 | 1/256 of f/1.4 | Very deep |

## Depth of Field Factors

1. **Aperture** -- wider aperture = shallower DOF
2. **Focal length** -- longer lens = shallower DOF
3. **Distance to subject** -- closer = shallower DOF
4. **Sensor size** -- larger sensor = shallower DOF

## Practical Applications

- **Portraits**: f/1.4-f/2.8 (blurred background)
- **Landscapes**: f/8-f/16 (everything sharp)
- **Macro**: f/11-f/16 (enough DOF)
"""
    elif "shutter speed" in t or "motion" in t:
        return f"""![Shutter Speed]({img})

## Shutter Speed and Motion

Shutter speed controls **how long the sensor is exposed to light**.

## Common Speeds

| Speed | Effect | Use Case |
|-------|--------|----------|
| 1/4000s | Freezes fast motion | Sports, birds |
| 1/500s | Freezes general motion | Street, portraits |
| 1/125s | Handheld general use | Everyday shooting |
| 1/30s | Risk of camera shake | Low light |
| 1" | Motion blur starts | Waterfalls, light trails |
| 30" | Extreme blur | Night, astro |

## The Reciprocal Rule

When handholding, use shutter speed at least 1/focal length.

50mm lens -> minimum 1/50s
200mm lens -> minimum 1/200s

## Creative Motion Effects

- **Panning**: Move camera with subject for sharp subject, blurred background
- **Long exposure**: Smooth water, streaking clouds, light trails
- **Bulb mode**: Hold shutter open for very long exposures
"""
    elif "iso" in t or "noise" in t:
        return f"""![ISO & Noise]({img})

## ISO and Noise

ISO measures the **sensitivity of your camera sensor to light**. Higher ISO amplifies the signal but also amplifies noise.

## ISO Ranges

| ISO | Light Condition | Image Quality |
|-----|-----------------|---------------|
| 100-200 | Bright sunlight | Excellent |
| 400-800 | Overcast, shade | Good |
| 1600-3200 | Indoor, evening | Noticeable noise |
| 6400+ | Low light, night | Significant noise |

## Types of Noise

- **Luminance noise** -- grainy appearance (can be pleasing)
- **Chromatic noise** -- coloured specks (usually undesirable)

## Noise Reduction Strategies

1. Expose properly (expose to the right)
2. Use wider aperture or slower shutter instead
3. Denoise in post-processing (Lightroom, Topaz)
4. Modern cameras handle high ISO better than ever

## Tips

- Keep ISO as low as possible while maintaining proper exposure
- Modern cameras can shoot clean images at ISO 3200+
- Noise is better than blur from camera shake
"""
    elif "rule of thirds" in t or "composition" in t:
        return f"""![Composition]({img})

## Rule of Thirds

The rule of thirds divides your frame into a **3x3 grid** of equal sections. Key elements should be placed along these lines or at their intersections.

## Using the Grid

Place subjects at intersection points for more dynamic compositions:

| Top-left | Top-right |
|----------|-----------|
| Strongest focal point | Secondary focal point |
| Bottom-left | Bottom-right |
| Third strongest | Least dynamic |

## Other Composition Techniques

| Technique | Description |
|-----------|-------------|
| Leading lines | Lines that guide the eye through the image |
| Symmetry | Balanced, mirror-like compositions |
| Framing | Use natural elements as frames |
| Negative space | Empty space around the subject |
| Patterns and textures | Repetition creates visual interest |
| Depth | Foreground, middleground, background |
"""
    elif "golden hour" in t or "golden" in t:
        return f"""![Golden Hour]({img})

## Golden Hour

Golden hour is the **period shortly after sunrise and before sunset** when the light is warm, soft, and directional.

## Characteristics

| Aspect | Description |
|--------|-------------|
| Colour temperature | Warm (3000-4000K) |
| Shadows | Long and soft |
| Contrast | Lower than midday |
| Direction | Low angle, side or back |
| Duration | About 1 hour (varies by location and season) |

## Golden Hour Photography Tips

1. **Plan ahead** -- use apps like PhotoPills or Sun Surveyor
2. **Arrive early** -- set up before the light is best
3. **Shoot with the sun** -- side/backlight creates depth
4. **Include the sun** -- lens flare can be artistic
5. **Switch to portrait** -- warm skin tones flatter subjects

## Blue Hour

The period of twilight when the sun is below the horizon. The sky takes on a deep blue tone. Perfect for cityscapes, lights, and moody landscapes.

- Civil twilight: sun 0-6 degrees below horizon
- Nautical twilight: sun 6-12 degrees below horizon
"""
    elif "studio lighting" in t or "studio" in t:
        return f"""![Studio Lighting]({img})

## Studio Lighting Setup

Studio lighting gives you **complete control over light direction, quality, and intensity**.

## Key Components

| Component | Purpose |
|-----------|---------|
| Key light | Main light source |
| Fill light | Fills shadows from key light |
| Back light | Separates subject from background |
| Background light | Illuminates the background |

## Lighting Patterns

| Pattern | Key Light Position | Effect |
|---------|-------------------|--------|
| Rembrandt | 45 degrees, above eye level | Triangle of light on cheek |
| Loop | 30-45 degrees, slightly above | Classic portrait |
| Butterfly | Directly in front, above | Glamour/fashion |
| Split | 90 degrees to side | Dramatic, moody |
| Broad | 45 degrees, illuminating the side facing camera | Widens the face |
| Short | 45 degrees, illuminating the side away from camera | Slims the face |

## Light Modifiers

- **Softbox** -- soft, diffused light
- **Umbrella** -- broad, soft light
- **Beauty dish** -- contrasty but soft
- **Snoot** -- narrow, hard light
- **Grid** -- directional, controlled light
"""
    elif "natural light" in t or "portrait" in t:
        return f"""![Natural Light]({img})

## Natural Light Portraits

Natural light portraiture uses **available light** (sunlight, window light) to create flattering portraits without artificial lighting.

## Best Natural Light for Portraits

| Light Source | Quality | Best For |
|-------------|---------|----------|
| Window light | Soft, directional | Indoor portraits |
| Open shade | Even, soft | Outdoor portraits |
| Golden hour | Warm, glowy | Dreamy portraits |
| Overcast | Soft, diffused | Even skin tones |

## Window Light Techniques

1. **Side lighting** -- place subject at 90 degrees to window
2. **45-degree lighting** -- subject at 45 degrees to window
3. **Front lighting** -- subject facing the window
4. **Back lighting** -- subject between you and window (silhouette)

## Reflectors

| Reflector Colour | Effect |
|-----------------|--------|
| White | Soft, natural fill |
| Silver | Bright, contrasty fill |
| Gold | Warm fill light |
| Black | Negative fill, deepens shadows |

Natural light is free, beautiful, and always available. Learn to see and shape it.
"""
    elif "lightroom" in t and "workflow" in t:
        return f"""![Lightroom Workflow]({img})

## Lightroom Workflow

Adobe Lightroom provides a **non-destructive editing workflow** for organising and processing photos.

## Import and Organise

1. Import photos (Copy as DNG or Copy)
2. Apply develop presets on import
3. Add keywords and metadata
4. Rate photos (P for pick, X for reject)
5. Create collections for projects

## Basic Adjustments

| Adjustment | Purpose |
|------------|---------|
| Exposure | Overall brightness |
| Contrast | Difference between light and dark |
| Highlights | Brightest areas |
| Shadows | Darkest areas |
| Whites | White point |
| Blacks | Black point |
| Clarity | Midtone contrast |
| Vibrance | Saturation of less-saturated colours |
| Saturation | Overall colour intensity |

## Tone Curve

Fine-tune contrast across the tonal range: Highlights, Lights, Darks, Shadows.

## HSL Panel

Adjust individual colour ranges: Hue, Saturation, Luminance.

## Detail Panel

- **Sharpening** -- enhance detail
- **Noise reduction** -- reduce luminance and colour noise

A consistent workflow saves time and ensures a cohesive look across your portfolio.
"""
    elif "color grading" in t or "colour grading" in t or "color" in t:
        return f"""![Color Grading]({img})

## Color Grading

Color grading is the **process of altering and enhancing the colours** of an image to create a specific mood or style.

## The Color Wheel

Primary colours: Red, Green, Blue
Secondary colours: Cyan, Magenta, Yellow

## Lightroom Color Grading Panel

The Color Grading panel (replaces Split Toning) lets you apply colour casts to:

- **Shadows** -- the darkest parts of the image
- **Midtones** -- the middle tonal range
- **Highlights** -- the brightest parts

## Popular Colour Palettes

| Palette | Description | Mood |
|---------|-------------|------|
| Orange-teal | Orange skin, teal shadows | Cinematic |
| Warm | Golden highlights, warm midtones | Cozy, nostalgic |
| Cool | Blue shadows, neutral highlights | Moody, clean |
| Desaturated | Low saturation, muted colours | Timeless, artistic |
| Vintage | Faded blacks, warm tones | Retro, film-like |
"""
    elif "skin retouching" in t or "retouching" in t:
        return f"""![Skin Retouching]({img})

## Skin Retouching

Skin retouching **enhances portraits by smoothing skin while preserving natural texture**.

## Non-Destructive Workflow

Always work on duplicate layers or adjustment layers in Photoshop.

## Frequency Separation

Separates texture (high frequency) from colour/tone (low frequency):

1. Duplicate background layer twice
2. Bottom copy: apply Gaussian Blur (low frequency)
3. Top copy: Apply Image -> subtract blurred layer (high frequency)
4. Set top layer to Linear Light blending mode
5. Retouch colour on low frequency layer
6. Retouch texture on high frequency layer

## Quick Fixes in Lightroom

| Tool | Use For |
|------|---------|
| Spot Removal | Blemishes, spots, dust |
| Adjustment Brush | Smooth skin areas |
| Graduated Filter | Even skin tone |

## Dodge and Burn

Lighten (dodge) and darken (burn) specific areas to enhance dimension:

- Dodge highlights on cheekbones, brow bone, nose bridge
- Burn shadows on jawline, eye creases, hair

Always zoom to 100% and check your work at full resolution.
"""
    elif "exporting" in t or "export" in t:
        return f"""![Exporting]({img})

## Exporting for Web and Print

Proper export settings ensure **your images look their best** on different mediums.

## Web Export Settings

| Setting | Recommendation |
|---------|---------------|
| File format | JPEG or PNG |
| Colour space | sRGB |
| Resolution | 72 ppi |
| Size | 1200-2000px on longest side |
| Quality | 80-90% (JPEG) |
| Sharpen | Screen (standard) |

## Print Export Settings

| Setting | Recommendation |
|---------|---------------|
| File format | TIFF or JPEG (max quality) |
| Colour space | Adobe RGB or ProPhoto RGB |
| Resolution | 300 ppi |
| Size | Actual print dimensions |
| Bit depth | 16-bit |
| Sharpen | Print (high/standard/matte/glossy) |

## File Naming

Use consistent naming: Project_Number_Description_Version.jpg

## Watermarking

Add a subtle watermark to protect your work online. Keep it small and in a corner.

Always proof before exporting. Zoom to 100% and check for artifacts, oversharpening, or colour shifts.
"""
    return ""


def _datascience_content(title, module, img):
    t = title.lower()
    if "pandas" in t or "dataframe" in t:
        return f"""![Pandas]({img})

## Pandas DataFrames

Pandas is the **primary data manipulation library in Python**. The DataFrame is a 2D labelled data structure.

## Creating DataFrames

```python
import pandas as pd

# From dictionary
df = pd.DataFrame({{
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["NYC", "LA", "Chicago"]
}})

# From CSV
df = pd.read_csv("data.csv")

# Basic info
print(df.shape)      # (rows, columns)
print(df.info())     # Column types and nulls
print(df.describe()) # Summary statistics
```

## Selecting Data

```python
# Column selection
df["name"]           # Series
df[["name", "age"]]  # DataFrame

# Row selection
df.iloc[0]           # First row by position
df.loc[0]            # First row by label
df.head(10)          # First 10 rows

# Filtering
df[df["age"] > 30]
df[(df["age"] > 25) & (df["city"] == "NYC")]
```
"""
    elif "data cleaning" in t or "cleaning" in t:
        return f"""![Data Cleaning]({img})

## Data Cleaning Techniques

Data cleaning is the **process of detecting and correcting corrupt or inaccurate records**.

## Common Issues

```python
# Check for missing values
df.isnull().sum()

# Drop missing
df.dropna(subset=["important_column"])

# Fill missing
df["age"].fillna(df["age"].median(), inplace=True)
df["category"].fillna("Unknown", inplace=True)
df["flag"].fillna(False, inplace=True)

# Forward/backward fill for time series
df["value"].fillna(method="ffill", inplace=True)
```

## Duplicates

```python
df.duplicated().sum()
df.drop_duplicates(inplace=True)
df.drop_duplicates(subset=["email"], keep="last")
```

## Outliers

```python
# Z-score method
from scipy import stats
z_scores = stats.zscore(df["price"])
df = df[abs(z_scores) < 3]

# IQR method
Q1 = df["price"].quantile(0.25)
Q3 = df["price"].quantile(0.75)
IQR = Q3 - Q1
df = df[(df["price"] >= Q1 - 1.5*IQR) & (df["price"] <= Q3 + 1.5*IQR)]
```

## Data Type Conversion

```python
df["date"] = pd.to_datetime(df["date"])
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["category"] = df["category"].astype("category")
```

Clean data is the foundation of reliable analysis.
"""
    elif "merging" in t or "grouping" in t or "merge" in t or "group" in t:
        return f"""![Merging & Grouping]({img})

## Merging and Grouping

Merging **combines datasets** based on common columns. Grouping **aggregates data by categories**.

## Merging DataFrames

```python
# Inner join
merged = pd.merge(df1, df2, on="user_id")

# Left join
merged = pd.merge(df1, df2, on="user_id", how="left")

# Outer join
merged = pd.merge(df1, df2, on="user_id", how="outer")

# Merge on different column names
merged = pd.merge(df1, df2, left_on="id", right_on="user_id")
```

## Grouping

```python
# Group by single column
df.groupby("category")["price"].mean()

# Multiple aggregations
df.groupby("category").agg({{
    "price": ["mean", "std", "min", "max"],
    "quantity": "sum"
}})

# Multiple groupby columns
df.groupby(["category", "region"])["revenue"].sum()

# Reset index after groupby
df.groupby("category")["price"].mean().reset_index()
```
"""
    elif "time series" in t or "time" in t:
        return f"""![Time Series]({img})

## Time Series Analysis

Time series analysis deals with **data points indexed in time order**.

## Working with Dates

```python
df["date"] = pd.to_datetime(df["date"])
df.set_index("date", inplace=True)

# Resampling
df.resample("D").mean()    # Daily
df.resample("W").sum()     # Weekly
df.resample("M").mean()    # Monthly
df.resample("Q").mean()    # Quarterly

# Rolling windows
df["rolling_avg"] = df["value"].rolling(window=7).mean()
df["rolling_std"] = df["value"].rolling(window=7).std()
```

## Common Analyses

```python
# Lag features
df["lag_1"] = df["value"].shift(1)
df["lag_7"] = df["value"].shift(7)

# Difference (remove trend)
df["diff"] = df["value"].diff()

# Cumulative
df["cumsum"] = df["value"].cumsum()
```

Time series analysis is essential for forecasting, anomaly detection, and trend analysis.
"""
    elif "matplotlib" in t:
        return f"""![Matplotlib]({img})

## Matplotlib Basics

Matplotlib is the **fundamental plotting library in Python**.

## Basic Plot Types

```python
import matplotlib.pyplot as plt

# Line plot
plt.plot(x, y)
plt.xlabel("X Label")
plt.ylabel("Y Label")
plt.title("Title")
plt.show()

# Bar chart
plt.bar(categories, values)

# Histogram
plt.hist(data, bins=30, edgecolor="black")

# Scatter plot
plt.scatter(x, y, alpha=0.5)

# Subplots
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
axes[0, 0].plot(x, y)
axes[0, 1].bar(cat, val)
```

## Customisation

```python
plt.style.use("seaborn-v0_8")
plt.figure(figsize=(12, 6))
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("plot.png", dpi=300, bbox_inches="tight")
```
"""
    elif "seaborn" in t:
        return f"""![Seaborn]({img})

## Seaborn Statistical Plots

Seaborn builds on Matplotlib to provide **beautiful statistical visualisations with minimal code**.

## Key Plots

```python
import seaborn as sns

# Distribution
sns.histplot(data=df, x="value", hue="category", kde=True)
sns.kdeplot(data=df, x="value", hue="category", fill=True)
sns.boxplot(data=df, x="category", y="value")

# Relationships
sns.scatterplot(data=df, x="age", y="income", hue="education")
sns.lineplot(data=df, x="date", y="sales", hue="region")

# Heatmap
sns.heatmap(df.corr(), annot=True, cmap="RdBu_r", center=0)

# Pairplot
sns.pairplot(df, hue="target")

# Categorical
sns.barplot(data=df, x="category", y="value")
sns.violinplot(data=df, x="category", y="value")
```
"""
    elif "plotly" in t or "interactive" in t:
        return f"""![Plotly]({img})

## Interactive Plotly Charts

Plotly creates **interactive, web-based visualisations** that users can zoom, pan, and hover over.

## Basic Plotly Express

```python
import plotly.express as px

# Scatter plot
fig = px.scatter(df, x="gdp_per_cap", y="life_exp",
                 size="population", color="continent",
                 hover_name="country", log_x=True)
fig.show()

# Line chart
fig = px.line(df, x="date", y="value", color="category")

# Bar chart
fig = px.bar(df, x="category", y="count", color="region",
             barmode="group")

# Histogram
fig = px.histogram(df, x="price", color="category",
                   marginal="box")
```

## Customisation

```python
fig.update_layout(
    title="Interactive Dashboard",
    xaxis_title="X Axis",
    yaxis_title="Y Axis",
    template="plotly_dark",
    hovermode="x unified"
)

fig.update_traces(marker=dict(size=8, line=dict(width=2, color="white")))
```
"""
    elif "streamlit" in t or "dashboard" in t:
        return f"""![Streamlit]({img})

## Dashboard with Streamlit

Streamlit lets you **turn data scripts into interactive web apps** with minimal effort.

## Basic App

```python
import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Data Dashboard")

df = pd.read_csv("data.csv")

# Sidebar filters
category = st.sidebar.selectbox("Category", df["category"].unique())
filtered = df[df["category"] == category]

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${filtered['revenue'].sum():,.0f}")
col2.metric("Avg Order", f"${filtered['amount'].mean():.2f}")
col3.metric("Orders", len(filtered))

# Chart
fig = px.line(filtered, x="date", y="revenue")
st.plotly_chart(fig, use_container_width=True)

# Data table
st.dataframe(filtered)
```

## Key Features

- `st.write()` -- write text, data, charts
- `st.sidebar` -- sidebar widgets
- `st.cache_data` -- cache expensive computations
- `st.session_state` -- persistent state across reruns
"""
    return ""


def _marketing_content(title, module, img):
    t = title.lower()
    if "keyword" in t:
        return f"""![Keyword Research]({img})

## Keyword Research

Keyword research is the **foundation of SEO and content marketing** -- understanding what your target audience searches for.

## The Keyword Research Process

1. **Brainstorm seed keywords** -- start with topics relevant to your business
2. **Expand with tools** -- use Google Keyword Planner, SEMrush, Ahrefs
3. **Analyse metrics** -- search volume, difficulty, CPC
4. **Group by intent** -- informational, navigational, transactional
5. **Prioritise** -- balance volume, difficulty, and relevance

## Keyword Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Search volume | Monthly searches | High |
| Keyword difficulty | Competition level | Low-Medium |
| CPC | Cost per click for ads | Context dependent |
| Intent | User's goal | Match content type |

## Keyword Types

| Type | Intent | Example |
|------|--------|---------|
| Short-tail | Broad | "shoes" |
| Mid-tail | Specific | "running shoes for women" |
| Long-tail | Very specific | "best trail running shoes for women 2024" |
"""

    elif "on-page" in t or "on page" in t:
        return f"""![On-Page SEO]({img})

## On-Page SEO

On-page SEO **optimises individual web pages** to rank higher and earn more relevant traffic.

## Key Elements

| Element | Best Practice |
|---------|---------------|
| Title tag | Include primary keyword near the start, under 60 chars |
| Meta description | Compelling summary with keyword, under 160 chars |
| URL structure | Short, descriptive, hyphen-separated |
| Headings (H1-H3) | Logical hierarchy with keywords |
| Image alt text | Descriptive with keywords |
| Internal links | Link to relevant pages within your site |
| Content quality | Comprehensive, original, valuable |

## Content Optimisation

- Keyword in first 100 words
- Use LSI (related) keywords naturally
- Include structured data (schema markup)
- Optimise for featured snippets
- Ensure readability (short paragraphs, bullet points)

## Technical On-Page

- Page speed (Core Web Vitals)
- Mobile responsiveness
- HTTPS security
- Canonical URLs
"""

    elif "link building" in t or "link build" in t:
        return f"""![Link Building]({img})

## Link Building

Link building is the **process of acquiring hyperlinks from other websites** to your own. It is a critical ranking factor.

## Link Quality Factors

| Factor | High Quality | Low Quality |
|--------|--------------|-------------|
| Authority | High DA/DR site | Low DA/spammy |
| Relevance | Same industry | Unrelated niche |
| Placement | Editorial, in-content | Footer, sidebar |
| Link type | Dofollow | Nofollow |
| Anchor text | Natural, varied | Exact match, over-optimised |

## Link Building Strategies

1. **Content marketing** -- create truly valuable content that naturally attracts links
2. **Guest posting** -- write for reputable sites in your industry
3. **Broken link building** -- find broken links, offer your content as replacement
4. **Skyscraper technique** -- find popular content, make something better
5. **Digital PR** -- earn mentions from journalists and bloggers
6. **Resource pages** -- get listed on industry resource lists

## What to Avoid

- Buying links (Google penalty risk)
- Private blog networks (PBNs)
- Excessive link exchanges
- Automated link building
"""

    elif "technical seo" in t or "seo audit" in t:
        return f"""![Technical SEO]({img})

## Technical SEO Audit

A technical SEO audit **evaluates the technical health of your website** to identify issues affecting search performance.

## Audit Checklist

| Area | What to Check | Tools |
|------|---------------|-------|
| Crawlability | Robots.txt, sitemap.xml | Screaming Frog |
| Indexability | Meta robots, canonical tags | Google Search Console |
| Page speed | Core Web Vitals (LCP, FID, CLS) | PageSpeed Insights |
| Mobile | Mobile-friendliness | Mobile-Friendly Test |
| Security | HTTPS, mixed content issues | SSL Labs |
| Structured data | Schema markup validation | Rich Results Test |
| Duplicate content | Canonicalisation issues | Site audit tools |
| Broken links | 404 errors, redirect chains | Crawl tools |

## Core Web Vitals

- **LCP (Largest Contentful Paint)** -- loading speed, target < 2.5s
- **FID (First Input Delay)** -- interactivity, target < 100ms
- **CLS (Cumulative Layout Shift)** -- visual stability, target < 0.1

A technical audit should be conducted quarterly to catch issues early.
"""

    elif "google ads" in t or "ads setup" in t or "ads" in t:
        return f"""![Google Ads]({img})

## Google Ads Setup

Google Ads (formerly AdWords) is **Google's pay-per-click (PPC) advertising platform**.

## Campaign Structure

```
Account
  +-- Campaign
       +-- Ad Group
       |    +-- Keywords
       |    +-- Ads
       +-- Ad Group
            +-- Keywords
            +-- Ads
```

## Campaign Types

| Type | Where Ads Appear | Best For |
|------|-----------------|----------|
| Search | Google search results | Intent-driven traffic |
| Display | Websites across Google's network | Brand awareness |
| Shopping | Product listings | E-commerce |
| Video | YouTube | Video marketing |
| App | Google Play, search | App installs |

## Key Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| CTR | Click-through rate | > 3% |
| CPC | Cost per click | As low as possible |
| Conversion rate | % who convert | Varies by industry |
| ROAS | Return on ad spend | > 400% |
| Quality Score | Google's ad quality rating | 7/10+ |
"""

    elif "meta ads" in t or "facebook ads" in t or "meta" in t:
        return f"""![Meta Ads]({img})

## Meta Ads Manager

Meta Ads Manager (Facebook and Instagram advertising) lets you **reach highly targeted audiences** based on demographics, interests, and behaviours.

## Campaign Structure

1. **Campaign** -- objective (awareness, consideration, conversion)
2. **Ad Set** -- targeting, budget, schedule
3. **Ad** -- creative (image, video, copy, CTA)

## Targeting Options

| Targeting Type | Description |
|----------------|-------------|
| Demographics | Age, gender, location, language |
| Interests | Hobbies, pages liked, activities |
| Behaviours | Purchase behaviour, device usage |
| Custom audiences | Website visitors, customer lists, engagement |
| Lookalike audiences | Similar to your best customers |

## Ad Formats

- **Image** -- single image with text
- **Video** -- engaging video content
- **Carousel** -- multiple images/videos swipeable
- **Collection** -- product catalogue showcase
- **Stories** -- full-screen vertical format
"""

    elif "retargeting" in t or "remarketing" in t:
        return f"""![Retargeting]({img})

## Retargeting Campaigns

Retargeting **shows ads to people who have visited your website** but did not convert.

## How Retargeting Works

1. User visits your website
2. A tracking pixel is placed in their browser
3. They see your ads as they browse other sites
4. They return and complete the desired action

## Retargeting Segments

| Segment | Time Window | Bid Strategy |
|---------|-------------|--------------|
| All visitors | 30 days | Lower bid |
| Product page visitors | 14 days | Medium bid |
| Cart abandoners | 7 days | Higher bid |
| Past customers | 90 days | Lower bid (cross-sell) |

## Best Practices

- **Frequency cap** -- limit ad exposure (3-5 per day)
- **Creative rotation** -- refresh ads regularly to avoid banner blindness
- **Exclude converters** -- don't show conversion ads to those who already converted
- **Dynamic retargeting** -- show the exact product they viewed
"""

    elif "roi" in t or "attribution" in t:
        return f"""![ROI & Attribution]({img})

## ROI and Attribution

Measuring **return on investment and attribution** is essential for proving marketing effectiveness.

## Calculating ROI

ROI = (Revenue - Cost) / Cost * 100

## Marketing Attribution Models

| Model | Description | Use Case |
|-------|-------------|----------|
| Last click | 100% credit to last touchpoint | Simple reporting |
| First click | 100% credit to first touchpoint | Brand awareness |
| Linear | Equal credit to all touchpoints | Balanced view |
| Time decay | More credit to recent touchpoints | Long sales cycles |
| Position-based | 40% first, 40% last, 20% middle | Full funnel view |
| Data-driven | Algorithmic credit分配 | Advanced analytics |

## Key Metrics

| Metric | Formula |
|--------|---------|
| CAC | Total sales cost / New customers |
| ROAS | Revenue from ads / Ad spend |
| LTV | Avg purchase value * Avg frequency * Avg customer lifespan |
| Payback period | CAC / (Monthly revenue per customer * Gross margin) |
"""

    elif "content calendar" in t or "content strategy" in t:
        return f"""![Content Calendar]({img})

## Content Calendar Strategy

A content calendar **plans, organises, and schedules your content production and distribution**.

## Calendar Structure

| Column | Description |
|--------|-------------|
| Date | Publish date |
| Topic | Content topic/title |
| Format | Blog, video, social post, email |
| Channel | Where it will be published |
| Status | Idea, draft, review, published |
| Owner | Person responsible |
| Keywords | Target SEO keywords |
| Goals | Traffic, leads, engagement |

## Content Mix

| Content Type | Percentage | Purpose |
|--------------|------------|---------|
| Educational | 40% | Build authority, attract new audience |
| Engaging | 25% | Build community, encourage sharing |
| Promotional | 20% | Drive conversions |
| Curated | 15% | Provide value with less resources |

## Planning Process

1. Set goals (traffic, leads, brand awareness)
2. Research topics (keyword research, competitor analysis)
3. Map to buyer's journey (awareness, consideration, decision)
4. Create content in batches
5. Schedule and publish consistently
6. Measure and iterate
"""

    elif "copywriting" in t or "copy" in t:
        return f"""![Copywriting]({img})

## Copywriting for Conversions

Copywriting is the **art and science of writing text that persuades people to take action**.

## The AIDA Formula

| Stage | What to Do | Example |
|-------|-----------|---------|
| Attention | Grab their interest | Headline that stops the scroll |
| Interest | Keep them reading | Benefits and features |
| Desire | Make them want it | Social proof, testimonials |
| Action | Tell them what to do | Clear CTA |

## Writing for the Web

- **Scannable** -- short paragraphs, bullet points, subheadings
- **Specific** -- concrete numbers and details over vague claims
- **Benefit-focused** -- "Save 10 hours per week" not "Our tool is efficient"
- **Action-oriented** -- active voice, strong verbs
- **Conversational** -- write like you speak (but more polished)

## CTA Best Practices

- Use command verbs: Get, Start, Try, Subscribe, Buy
- Create urgency: Limited time, Limited spots
- Reduce friction: Free, No credit card, Cancel anytime
- Be specific: "Start your 14-day free trial" vs "Sign up"
"""

    elif "email sequences" in t or "email" in t:
        return f"""![Email Sequences]({img})

## Email Sequences

Email sequences are **automated series of emails sent based on triggers or timelines**.

## Types of Sequences

| Sequence | Trigger | Goal |
|----------|---------|------|
| Welcome | New subscriber | Onboard, set expectations |
| Onboarding | New user | Drive activation |
| Nurture | Lead download | Build trust, educate |
| Abandoned cart | Cart created, not purchased | Recover lost sales |
| Re-engagement | Inactive for 90+ days | Win back |
| Post-purchase | Purchase completed | Upsell, cross-sell |

## Welcome Email Sequence

1. **Day 0**: Welcome + deliver lead magnet
2. **Day 2**: Share your story and mission
3. **Day 5**: Best content/resources
4. **Day 8**: Case study or social proof
5. **Day 12**: Offer/pitch with urgency

## Best Practices

- Personalise subject lines (open rates +26%)
- Segment your list (targeted emails perform better)
- Test send times and days
- Monitor open rates, click rates, and unsubscribes
- Clean your list regularly
"""

    elif "analytics" in t or "ga4" in t:
        return f"""![Analytics]({img})

## Analytics with GA4

Google Analytics 4 (GA4) is the **latest generation of Google Analytics**, focused on cross-platform tracking and event-based data.

## Key Differences from Universal Analytics

| Aspect | Universal Analytics | GA4 |
|--------|-------------------|-----|
| Data model | Session-based | Event-based |
| Tracking | Page views | Events + parameters |
| Cross-platform | Separate properties | Single property |
| Reporting | Pre-defined reports | Explorations |
| Privacy | Cookie-dependent | Cookieless future ready |

## Key Metrics

| Metric | Definition |
|--------|------------|
| Users | Number of unique visitors |
| Sessions | Number of visits |
| Engagement rate | % of sessions lasting > 10 seconds |
| Events | Any tracked interaction |
| Conversions | Key events you define as valuable |

## Setting Up GA4

1. Create GA4 property in Google Analytics
2. Add measurement ID to your website
3. Set up events (recommended + custom)
4. Configure conversions
5. Link to Google Search Console and Google Ads
"""

    return ""


def _business_content(title, module, img, is_vc=False):
    t = title.lower()
    if is_vc:
        if "how vc" in t or "vc fund" in t or "fund" in t:
            return f"""![VC Funds]({img})

## How VC Funds Work

Venture capital funds are **pooled investment vehicles that invest in early-stage, high-growth companies**.

## Fund Structure

Limited Partners (LPs) provide capital. General Partner (GP) manages the fund. The fund invests in 10-25 portfolio companies over its life.

## Fund Economics

| Metric | Typical Value |
|--------|---------------|
| Fund size | $50M - $500M+ |
| Management fee | 2% annually |
| Carried interest | 20% of profits |
| Fund life | 10 years |

## Investment Stages

| Stage | Check Size | Risk |
|-------|------------|------|
| Seed | $500K-$2M | Very High |
| Series A | $2M-$15M | High |
| Series B | $15M-$50M | Medium |
| Series C+ | $50M+ | Lower |

VC funds are high-risk, high-reward. Most companies fail, but successes return the entire fund.
"""
        elif "deal sourcing" in t:
            return f"""![Deal Sourcing]({img})

## Deal Sourcing

Deal sourcing is the **process of identifying and evaluating potential investment opportunities**.

## Sourcing Channels

| Channel | Quality | Volume |
|---------|---------|--------|
| Warm introductions | Highest | Low |
| Founder outreach | High | Medium |
| Conferences | Medium | High |
| Accelerators | Medium-High | Medium |
| Cold inbound | Variable | Very High |

## The Funnel

Sourced: 1,000 deals -> Met: 200 -> Deep dive: 50 -> Term sheet: 10 -> Invested: 5

## Evaluation Criteria

1. **Team** -- founder-market fit, experience
2. **Market** -- size, growth rate, timing
3. **Product** -- differentiation, defensibility
4. **Traction** -- revenue, users, growth
5. **Business model** -- unit economics, margins

Top-tier VCs see thousands of deals per year but invest in only a handful.
"""
        elif "due diligence" in t:
            return f"""![Due Diligence]({img})

## Due Diligence

Due diligence is the **comprehensive investigation of a company before making an investment**.

## Key Areas

| Area | What to Check |
|------|---------------|
| Financial | Revenue, burn rate, unit economics |
| Legal | IP ownership, contracts, compliance |
| Technical | Architecture, code quality, security |
| Market | TAM/SAM/SOM, competition |
| Team | Background checks, references |
| Product | Roadmap, user feedback, retention |

## The Process

1. Request data room
2. Review materials
3. Customer calls (reference checks)
4. Technical review (code audit)
5. Legal review (contracts, IP, cap table)
6. Summarise findings (risk assessment)

## Common Deal Killers

Untenable cap table, misaligned founders, IP not assigned, customer concentration > 50%, unclear path to profitability.
"""
        elif "cap table" in t or "cap" in t:
            return f"""![Cap Table]({img})

## Cap Table Basics

A capitalization table (cap table) shows **who owns what in a company** -- founders, employees, investors, and option pools.

## Sample Cap Table

| Stakeholder | Shares | % Own |
|-------------|--------|-------|
| Founder A | 5,000,000 | 45.0% |
| Founder B | 3,000,000 | 27.0% |
| Employee Pool | 1,500,000 | 13.5% |
| Seed VC | 1,100,000 | 10.0% |
| **Total** | **11,100,000** | **100%** |

## Key Terms

| Term | Definition |
|------|------------|
| Authorised shares | Total shares company can issue |
| Issued shares | Shares currently owned |
| Fully diluted | All shares + options + warrants + converts |
| Option pool | Shares reserved for employee grants |

## Dilution

Each funding round dilutes existing shareholders. Founders often end up with 10-20% after multiple rounds, but the value of that ownership ideally increases.
"""
        elif "pre-money" in t or "post-money" in t or "valuation" in t:
            return f"""![Valuation]({img})

## Pre-money vs Post-money

Post-money Valuation = Pre-money Valuation + Investment Amount

## Example

Pre-money: $8M
Investment: $2M
Post-money: $10M
Investor ownership: $2M / $10M = 20%

## Valuation Methods

| Method | Approach | Best For |
|--------|----------|----------|
| Berkus Method | Qualitative assessment of 5 key areas | Pre-revenue |
| Scorecard Method | Compare to average startup | Seed stage |
| VC Method | Work backwards from exit | Series A+ |
| Comparable Analysis | Market multiples | Later stages |

## The VC Valuation Method

Required ownership = (Target return * Investment) / Expected exit value
Post-money = Investment / Required ownership
Pre-money = Post-money - Investment
"""
        elif "term sheet" in t:
            return f"""![Term Sheet]({img})

## Term Sheet Negotiation

A term sheet outlines the **key terms of an investment** and sets the framework for final legal agreements.

## Key Economic Terms

| Term | Founder-Friendly |
|------|-----------------|
| Valuation | Higher is better |
| Liquidation Preference | 1x non-participating |
| Anti-dilution | Weighted average |
| Option Pool | Smaller pool = less dilution |
| Vesting | 4-year with 1-year cliff |

## Key Control Terms

| Term | What It Means |
|------|---------------|
| Board Composition | Who controls the board |
| Protective Provisions | Investor veto rights |
| Drag-Along Rights | Force minority to join a sale |
| Information Rights | Access to financial reports |

## Negotiation Tips

1. Know your BATNA (best alternative)
2. Focus on economics (valuation, liquidation, option pool)
3. Understand control terms (board matters more than you think)
4. Get a good lawyer
5. Don't optimise for price alone -- best investor brings more than money
"""
        elif "dilution" in t or "option" in t:
            return f"""![Dilution & Options]({img})

## Dilution and Options

Dilution is the **reduction in ownership percentage** when new shares are issued. Options are the primary tool for attracting talent.

## How Dilution Works

Founding: Founder 100%
Round 1: Founder 60%, Investors 20%, Option Pool 20%
Round 2: Founder 42%, Investors 35%, Option Pool 15%, Employees 8%

## Option Pool Mechanics

The option pool is created before a funding round, so dilution is absorbed by existing shareholders.

## Employee Stock Options

| Feature | Typical |
|---------|---------|
| Shares | 10,000-100,000 |
| Vesting | 4 years, 1-year cliff |
| Exercise price | FMV at grant (409A valuation) |
| ISO vs NSO | Different tax treatment |

## Managing Dilution

- Plan for 3-4 rounds of dilution before exit
- 10% of $1B is better than 100% of a lifestyle business
"""
        elif "safe" in t or "priced" in t:
            return f"""![SAFE vs Priced]({img})

## SAFE vs Priced Rounds

SAFEs (Simple Agreement for Future Equity) and priced rounds are the two main ways startups raise capital.

## SAFE Features

| Feature | Description |
|---------|-------------|
| Valuation cap | Maximum valuation at conversion |
| Discount rate | 15-25% off next round price |
| MFN clause | Most Favoured Nation protection |
| Maturity date | None (SAFE is not debt) |

## Priced Round Features

Negotiated valuation, board seats, liquidation preference, anti-dilution, and full legal documentation. More complex and expensive but provides clarity.

## SAFE vs Priced

| Aspect | SAFE | Priced Round |
|--------|------|--------------|
| Legal cost | $2K-$5K | $20K-$50K+ |
| Time to close | Days | Weeks |
| Valuation | Deferred | Set now |
| Complexity | Low | High |
| Best for | Seed (< $2M) | Series A+ |
"""
        return f"""![VC]({img})

## {title}

This lesson covers **{title}** within the Venture Capital module.

Understanding venture capital mechanics is essential for building and financing high-growth companies.

## Key Concepts

- Fund structures and economics
- Deal sourcing and due diligence
- Valuation and term sheet negotiation
- Portfolio management and exits

## Learning Objectives

- Understand the fundamentals of venture capital
- Apply concepts to real-world startup scenarios
- Make informed decisions about fundraising and company building
"""
    else:
        # Business strategy
        if "porter" in t or "forces" in t:
            return f"""![Porter 5 Forces]({img})

## Porter's Five Forces

A **framework for analysing industry competition and profitability**.

## The Five Forces

1. **Rivalry** -- competition among existing firms
2. **New Entrants** -- ease of entering the market
3. **Substitutes** -- alternative products/services
4. **Supplier Power** -- leverage of suppliers
5. **Buyer Power** -- leverage of customers

## Applying the Framework

| Force | Strong Threat Means | Strategy |
|-------|-------------------|----------|
| Rivalry | Many competitors, slow growth | Differentiate |
| New Entrants | Low barriers | Build moat |
| Substitutes | Low switching costs | Lock-in |
| Supplier Power | Few suppliers | Vertical integration |
| Buyer Power | Few buyers | Build loyalty |

Porter's Five Forces helps you understand industry structure and develop competitive strategy.
"""
        elif "swot" in t:
            return f"""![SWOT]({img})

## SWOT Analysis

SWOT analysis evaluates **Strengths, Weaknesses, Opportunities, and Threats**.

## The SWOT Matrix

| | Positive | Negative |
|--|----------|----------|
| Internal | **Strengths** (what you do well) | **Weaknesses** (areas to improve) |
| External | **Opportunities** (market trends) | **Threats** (external risks) |

## Example

| Strengths | Weaknesses |
|-----------|------------|
| Strong brand recognition | High operational costs |
| Patented technology | Limited geographic reach |
| Experienced leadership team | Dependence on key suppliers |

| Opportunities | Threats |
|---------------|---------|
| Emerging markets | New competitors |
| Digital transformation | Regulatory changes |
| Strategic partnerships | Economic downturn |

## How to Use SWOT

1. Be honest and specific
2. Prioritise the most important items
3. Use strengths to capture opportunities
4. Address weaknesses that expose you to threats
5. Create action plans for each quadrant
"""
        elif "business model canvas" in t or "bmc" in t or "canvas" in t:
            return f"""![Business Model Canvas]({img})

## Business Model Canvas

The Business Model Canvas is a **strategic management template for developing new or documenting existing business models**.

## The 9 Building Blocks

| Block | Description | Example |
|-------|-------------|---------|
| Customer Segments | Who you serve | Young professionals |
| Value Proposition | What you offer | Save time and money |
| Channels | How you deliver | Mobile app, website |
| Customer Relationships | How you interact | Self-service, chat |
| Revenue Streams | How you make money | Subscription, ads |
| Key Resources | What you need | Technology, team |
| Key Activities | What you do | Development, marketing |
| Key Partnerships | Who helps you | API providers, agencies |
| Cost Structure | What it costs | Salaries, hosting |

## Why Use It

- Single-page overview of your entire business
- Identifies gaps and dependencies
- Easy to iterate and pivot
- Aligns the team around one vision
"""
        elif "value proposition" in t or "value" in t:
            return f"""![Value Proposition]({img})

## Value Proposition Design

A value proposition is the **reason customers choose your product over alternatives**.

## Value Proposition Canvas

| Side | Component | Description |
|------|-----------|-------------|
| Customer Profile | Gains | What customers want to achieve |
| Customer Profile | Pains | What frustrates customers |
| Customer Profile | Jobs | What customers are trying to do |
| Value Map | Gain Creators | How you create benefits |
| Value Map | Pain Relievers | How you solve frustrations |
| Value Map | Products/Services | What you offer |

## Fit

Value proposition is achieved when:

Your Gain Creators match Customer Gains
Your Pain Relievers match Customer Pains
Your Products/Services match Customer Jobs

## Testing Your Value Proposition

1. State your hypothesis clearly
2. Create a minimum viable product (MVP)
3. Test with real customers
4. Measure willingness to pay
5. Iterate based on feedback
"""
        elif "product-market fit" in t or "pmf" in t:
            return f"""![Product-Market Fit]({img})

## Finding Product-Market Fit

Product-market fit is when **your product satisfies a strong market demand**.

## Signs of PMF

- Strong organic growth (word of mouth)
- High retention rates
- Users are disappointed when the product is unavailable
- Short sales cycles
- Inbound demand exceeds outbound efforts

## The PMF Survey

Ask users: "How would you feel if you could no longer use our product?"

- Very disappointed = 40%+ = strong PMF
- Somewhat disappointed = good PMF
- Not disappointed = no PMF

## Finding PMF

1. Start with a narrow market niche
2. Talk to users obsessively
3. Iterate based on feedback
4. Focus on retention, not acquisition
5. Be willing to pivot if needed

PMF is the most important milestone for any startup. Do not scale before achieving it.
"""
        elif "fundraising" in t or "fundraising 101" in t:
            return f"""![Fundraising]({img})

## Fundraising 101

Fundraising is the **process of raising capital from investors to grow your business**.

## When to Raise

| Stage | Focus | Typical Amount |
|-------|-------|----------------|
| Pre-seed | Idea, team | $100K-$500K |
| Seed | MVP, early traction | $500K-$2M |
| Series A | Product-market fit | $2M-$15M |
| Series B | Scaling | $15M-$50M |

## The Fundraising Process

1. Prepare materials (pitch deck, financial model, data room)
2. Build target list of investors
3. Warm introductions (best way in)
4. Pitch meetings (20-30 meetings)
5. Due diligence
6. Term sheet and close

## What Investors Look For

- Large market (TAM > $1B)
- Strong team (founder-market fit)
- Traction (revenue, users, growth)
- Defensibility (moat, tech, network effects)
- Clear business model (unit economics)

Fundraising is a full-time job. Plan for 3-6 months and prepare for rejection.
"""
        elif "team building" in t or "team" in t:
            return f"""![Team Building]({img})

## Team Building

Building a strong team is the **most important factor in startup success**.

## Hiring Principles

| Principle | Why It Matters |
|-----------|---------------|
| Hire for attitude, train for skill | Skills can be taught, values cannot |
| Prioritise communication | Startups change direction constantly |
| Look for ownership mentality | Need people who act like founders |
| Diversity of thought | Different perspectives drive innovation |
| Slow to hire, fast to fire | Bad hires are exponentially costly |

## Team Stages (Tuckman Model)

1. **Forming** -- getting to know each other
2. **Storming** -- conflict and disagreements
3. **Norming** -- establishing norms and processes
4. **Performing** -- high-functioning team

## Building Culture

- Define core values early
- Lead by example
- Celebrate wins (big and small)
- Create psychological safety
- Communicate transparently

Your team will outlast your product, your funding, and your market. Invest in it accordingly.
"""
        elif "growth hacking" in t or "growth" in t:
            return f"""![Growth Hacking]({img})

## Growth Hacking

Growth hacking is **experimenting across marketing, product, and sales to find the most effective ways to grow**.

## The Growth Process

1. **Analyse** -- find growth opportunities in data
2. **Ideate** -- brainstorm potential growth experiments
3. **Prioritise** -- ICE score (Impact, Confidence, Ease)
4. **Test** -- run experiments with clear metrics
5. **Scale** -- invest in what works

## Common Growth Hacks

| Tactic | Channel | Difficulty |
|--------|---------|------------|
| Referral program | Viral | Medium |
| Content SEO | Organic | Low |
| Social sharing | Viral | Low |
| Freemium model | Product | High |
| Integration partnerships | Distribution | Medium |

## Key Metrics

- **CAC** -- Customer Acquisition Cost
- **LTV** -- Lifetime Value
- **Virality coefficient** -- how many users each user brings
- **Activation rate** -- % who reach "aha" moment
- **Retention rate** -- % who come back

Growth hacking is a mindset, not a toolkit. Always be testing.
"""
        return f"""![Business]({img})

## {title}

This lesson covers **{title}** within the **{module}** module.

Understanding business strategy is essential for building and scaling successful companies.

## Learning Objectives

- Understand the core concepts of {title}
- Apply frameworks to real-world scenarios
- Make better strategic decisions

## Summary

Mastering {title} builds your strategic thinking and enables you to create more value.
"""


def _brand_content(title, module, img):
    t = title.lower()
    if "discovery" in t or "workshop" in t:
        return f"""![Brand Discovery]({img})

## Brand Discovery Workshop

A brand discovery workshop is the **foundational step in creating a brand identity**.

## Workshop Agenda

1. **Stakeholder interviews** -- understand business goals
2. **Brand audit** -- review existing materials
3. **Competitive landscape** -- analyse competitors
4. **Audience definition** -- who are we talking to?
5. **Brand archetype** -- define brand personality
6. **Vision and mission** -- why do we exist?

## Key Questions

- What is our purpose beyond profit?
- Who are our customers and what do they value?
- How do we want customers to feel?
- What makes us different from competitors?
- What are our core values?

## Deliverables

- Brand brief
- Audience personas
- Competitive analysis report
- Brand strategy document

A thorough discovery process prevents costly mistakes later in the design process.
"""
    elif "competitive analysis" in t or "competitive" in t:
        return f"""![Competitive Analysis]({img})

## Competitive Analysis

Competitive analysis identifies **your competitors and evaluates their strategies** to identify opportunities.

## Analysis Framework

| Aspect | What to Look For |
|--------|-----------------|
| Brand positioning | How they position themselves |
| Visual identity | Logo, colours, typography |
| Voice and tone | How they communicate |
| Target audience | Who they serve |
| Strengths | What they do well |
| Weaknesses | Where they fall short |
| Market share | Their presence in the market |

## Tools

- SWOT analysis for each competitor
- Brand perception survey
- Social media monitoring
- Website and content analysis

## Outcome

Identify gaps in the market that your brand can fill. Find opportunities to differentiate.
"""
    elif "positioning" in t or "differentiation" in t:
        return f"""![Positioning]({img})

## Positioning and Differentiation

Brand positioning is **how you want your brand to be perceived** relative to competitors.

## Positioning Statement

For [target audience], [brand name] is the [category] that [key benefit] because [reason to believe].

## Differentiation Strategies

| Strategy | Example |
|----------|---------|
| Product features | "The only one with..." |
| Price | Luxury or budget |
| Customer service | "We answer in 5 minutes" |
| Design | Apple's minimalist aesthetic |
| Experience | "Feel the difference" |
| Values | Patagonia's environmental focus |

## Perceptual Map

Map your brand and competitors on two key dimensions (e.g., price vs quality, traditional vs modern). Find white space where you can own a unique position.

Effective positioning makes every marketing decision easier because you know what you stand for.
"""
    elif "moodboard" in t or "mood boarding" in t:
        return f"""![Moodboard]({img})

## Moodboarding

Moodboards are **collages of images, colours, textures, and typography** that capture the visual direction of a brand.

## What to Include

| Element | Purpose |
|---------|---------|
| Colour palette | Mood and personality |
| Typography examples | Font styles and pairings |
| Photography | Style, lighting, mood |
| Textures | Physical feel |
| Iconography | Graphic style |
| Keywords | Descriptive words |

## Creating a Moodboard

1. Collect inspiration from various sources (Pinterest, Dribbble, magazines)
2. Focus on feeling and emotion, not literal designs
3. Edit ruthlessly -- remove anything that doesn't fit
4. Look for patterns and themes
5. Share with stakeholders for alignment

Moodboards align the team on the visual direction before design begins.
"""
    elif "logo design" in t or "logo" in t:
        return f"""![Logo Design]({img})

## Logo Design Process

A logo is the **visual cornerstone of your brand identity**.

## Logo Types

| Type | Description | Example |
|------|-------------|---------|
| Wordmark | Text-based | Google, Coca-Cola |
| Lettermark | Initials | IBM, HBO |
| Pictorial | Icon-based | Apple, Twitter |
| Abstract | Geometric symbol | Nike, Pepsi |
| Combination | Text + symbol | Adidas, Burger King |
| Emblem | Badge-style | Starbucks, NFL |

## Design Process

1. **Research** -- understand the brand, industry, and competitors
2. **Sketch** -- 50+ rough concepts on paper
3. **Digitise** -- refine 3-5 directions in vector
4. **Present** -- show concepts with context (mockups)
5. **Refine** -- iterate based on feedback
6. **Deliver** -- final files in multiple formats

## Essential Logo Qualities

- **Simple** -- recognisable at small sizes
- **Memorable** -- distinctive and unique
- **Timeless** -- avoid trends that date quickly
- **Versatile** -- works in black/white, small/large
- **Relevant** -- appropriate for the industry
"""
    elif "typography" in t:
        return f"""![Typography]({img})

## Typography System

Typography is the **art and technique of arranging type** to make written language legible, readable, and visually appealing.

## Type Classification

| Category | Examples | Character |
|----------|----------|-----------|
| Serif | Times New Roman, Garamond | Traditional, authoritative |
| Sans-serif | Helvetica, Inter | Modern, clean |
| Script | Pacifico, Brush Script | Elegant, decorative |
| Display | Impact, Abril Fatface | Headlines, attention-grabbing |
| Monospace | Courier, Fira Code | Technical, coding |

## Building a Type System

1. Choose a primary typeface for body text (readable)
2. Choose a secondary typeface for headings (distinctive)
3. Define hierarchy: H1, H2, H3, Body, Small
4. Set sizes, line heights, and letter spacing
5. Limit to 2-3 typefaces maximum

## Typography Tips

- Line length: 45-75 characters
- Line height: 1.5x for body text
- Scale: Use a modular scale (1.25 or 1.333)
- Contrast: Headings should be clearly distinct from body
"""
    elif "color palette" in t or "colour palette" in t or "palette" in t:
        return f"""![Color Palette]({img})

## Color Palette

Colour is one of the **most powerful tools in brand identity** -- it evokes emotion and creates recognition.

## Colour Psychology

| Colour | Emotion | Use Case |
|--------|---------|----------|
| Red | Excitement, urgency | Food, retail |
| Blue | Trust, calm | Finance, tech |
| Green | Nature, growth | Environment, health |
| Yellow | Optimism, warmth | Children, hospitality |
| Purple | Luxury, creativity | Beauty, premium |
| Orange | Energy, fun | Entertainment |
| Black | Sophistication, power | Luxury, fashion |
| White | Purity, simplicity | Healthcare, minimalism |

## Building a Colour System

| Colour Role | Description |
|-------------|-------------|
| Primary | Main brand colour |
| Secondary | Complementary accent |
| Neutral | Greys for text and backgrounds |
| Success | Green for positive states |
| Warning | Orange/amber for warnings |
| Error | Red for errors |

## Accessibility

Ensure proper contrast ratios (WCAG AA: 4.5:1 for text). Never rely on colour alone to convey information.
"""
    elif "photography style" in t or "photography" in t:
        return f"""![Photography Style]({img})

## Photography Style for Brand

A consistent photography style **reinforces brand identity** across all visual touchpoints.

## Defining Your Photography Style

| Dimension | Options |
|-----------|---------|
| Lighting | Natural, studio, dramatic, soft |
| Colour | Warm, cool, desaturated, vibrant |
| Composition | Candid, posed, minimal, detailed |
| Subject | People, products, lifestyle, abstract |
| Mood | Happy, serious, aspirational, authentic |

## Brand Photography Guidelines

- Define dos and don'ts for photo selection
- Create a lighting and colour reference
- Specify preferred angles and compositions
- Include examples of approved imagery
- Provide retouching parameters

## Stock Photography Tips

Avoid overly staged or generic stock photos. Look for authentic, diverse imagery that feels genuine. Consider investing in custom photoshoots for key brand materials.
"""
    elif "brand guidelines" in t or "guidelines" in t:
        return f"""![Brand Guidelines]({img})

## Brand Guidelines Structure

Brand guidelines are the **rules and standards for how a brand is presented** across all touchpoints.

## What to Include

| Section | Content |
|---------|---------|
| Brand story | Mission, vision, values, personality |
| Logo usage | Clear space, minimum size, incorrect uses |
| Colour palette | Hex, RGB, CMYK values for all colours |
| Typography | Fonts, sizes, hierarchy, line spacing |
| Imagery | Photography style, iconography, illustration |
| Voice and tone | Writing style, vocabulary, dos and don'ts |
| Applications | Stationery, social media, advertising, packaging |

## Why Guidelines Matter

- **Consistency** -- recognisable brand across all channels
- **Efficiency** -- designers and partners know the rules
- **Scalability** -- new team members can produce on-brand work
- **Protection** -- prevents brand dilution

Brand guidelines should be detailed enough to ensure consistency but flexible enough to allow creativity.
"""
    elif "component library" in t or "component" in t:
        return f"""![Component Library]({img})

## Component Library

A component library is a **collection of reusable UI elements** that implement brand styles.

## What Goes in a Library

| Component | Description |
|-----------|-------------|
| Buttons | Primary, secondary, tertiary, sizes, states |
| Forms | Input fields, select, checkbox, radio, toggle |
| Navigation | Header, sidebar, tabs, breadcrumbs |
| Cards | Product, profile, article variants |
| Modals | Dialog, alert, confirmation |
| Typography | All text styles as components |
| Icons | Consistent icon set |

## Benefits

- Design consistency across products
- Faster design and development
- Easier maintenance (update once, propagate everywhere)
- Shared language between design and development

## Tools

Figma for design components, Storybook for development components.
"""
    elif "client presentation" in t or "presentation" in t:
        return f"""![Client Presentation]({img})

## Client Presentation

Presenting brand work to clients is a **critical skill** for designers and agencies.

## Presentation Structure

1. **Recap** -- remind them of the brief and goals
2. **Discovery insights** -- share what you learned
3. **The strategy** -- explain the thinking behind the work
4. **The design** -- present the visual identity
5. **Rationale** -- explain every decision
6. **Applications** -- show it in context (mockups)
7. **Next steps** -- what happens after approval

## Tips for a Great Presentation

- Start with the strategy, not the design
- Show mockups (context sells the work)
- Explain the "why" behind every decision
- Be confident but open to feedback
- Prepare for tough questions

## Handling Feedback

- Listen fully before responding
- Ask clarifying questions
- Separate opinion from objective issues
- Know when to push back and when to adapt
"""
    elif "brand rollout" in t or "rollout" in t:
        return f"""![Brand Rollout]({img})

## Brand Rollout

A brand rollout is the **process of implementing the new brand identity** across all touchpoints.

## Rollout Phases

| Phase | Activities | Duration |
|-------|------------|----------|
| Internal launch | Employee training, internal comms | 1-2 weeks |
| Digital update | Website, social media, email | 2-4 weeks |
| Physical update | Signage, packaging, stationery | 4-8 weeks |
| External launch | PR, advertising, events | 1-2 weeks |

## Rollout Checklist

- [ ] Update website and digital properties
- [ ] Update social media profiles
- [ ] Create new email signatures and templates
- [ ] Print new business cards and stationery
- [ ] Update signage (office, store, vehicles)
- [ ] Update packaging and product labels
- [ ] Update internal documents and templates
- [ ] Train team on new brand guidelines
- [ ] Announce to customers and stakeholders
- [ ] Monitor and enforce consistency

## Managing Transition

- Plan for a phased rollout to minimise disruption
- Communicate clearly with all stakeholders
- Have a transition period where old and new coexist
- Celebrate the launch internally and externally
"""
    return ""


def generate_content(lesson_title, module_title, course_title):
    img = _image_url(lesson_title)
    course_lower = course_title.lower()
    module_lower = module_title.lower()

    if "python" in course_lower or "bootcamp" in course_lower:
        content = _python_content(lesson_title, module_title, img)
    elif "full-stack" in course_lower or "react & django" in course_lower:
        content = _fullstack_content(lesson_title, module_title, img)
    elif "advanced react" in course_lower or "react" in course_lower:
        content = _advanced_react_content(lesson_title, module_title, img)
    elif "design" in course_lower or "ux" in course_lower or "ui" in course_lower:
        content = _design_content(lesson_title, module_title, img)
    elif "machine learning" in course_lower or "ai" in course_lower:
        content = _ml_content(lesson_title, module_title, img)
    elif "photography" in course_lower:
        content = _photography_content(lesson_title, module_title, img)
    elif "data science" in course_lower:
        content = _datascience_content(lesson_title, module_title, img)
    elif "digital marketing" in course_lower or "marketing" in course_lower:
        content = _marketing_content(lesson_title, module_title, img)
    elif "brand identity" in course_lower or "brand" in course_lower:
        content = _brand_content(lesson_title, module_title, img)
    elif "venture capital" in course_lower:
        content = _business_content(lesson_title, module_title, img, is_vc=True)
    elif "business" in course_lower or "entrepreneurship" in course_lower:
        content = _business_content(lesson_title, module_title, img, is_vc=False)
    elif "landscape" in course_lower or "nature" in course_lower:
        content = _photography_content(lesson_title, module_title, img)
    else:
        content = _python_content(lesson_title, module_title, img)

    if content:
        return content

    # Fallback content
    return f"""![{lesson_title}]({img})

## {lesson_title}

This lesson covers **{lesson_title}** within the **{module_title}** module of the **{course_title}** course.

## Learning Objectives

By the end of this lesson, you will be able to:

- Understand the core concepts and principles of {lesson_title}
- Apply these concepts in practical scenarios
- Evaluate different approaches and choose the best one
- Build on this knowledge in subsequent lessons

## Key Takeaways

| Concept | Importance |
|---------|------------|
| Fundamentals | Building block for advanced topics |
| Practical Skills | Real-world problem solving |
| Best Practices | Professional quality work |

## Summary

Mastering {lesson_title} is an important step in your learning journey. Practice regularly and apply these concepts to real projects for deeper understanding.
"""


def get_lesson_type(title):
    if title in PDF_LESSONS:
        return "PDF"
    return "VIDEO"


QUIZ_TEMPLATES = {
    "Python Fundamentals": {
        "passing_score": 70,
        "description": "Test your understanding of Python basics including syntax, data types, and control flow.",
        "questions": [
            {
                "text": "What is the output of `print(type(42))`?",
                "choices": [
                    {"text": "<class 'int'>", "is_correct": True},
                    {"text": "<class 'float'>", "is_correct": False},
                    {"text": "<class 'str'>", "is_correct": False},
                    {"text": "<class 'number'>", "is_correct": False},
                ]
            },
            {
                "text": "Which of the following is a mutable data type in Python?",
                "choices": [
                    {"text": "List", "is_correct": True},
                    {"text": "Tuple", "is_correct": False},
                    {"text": "String", "is_correct": False},
                    {"text": "Integer", "is_correct": False},
                ]
            },
            {
                "text": "What does the `break` statement do in a loop?",
                "choices": [
                    {"text": "Exits the loop immediately", "is_correct": True},
                    {"text": "Skips the current iteration", "is_correct": False},
                    {"text": "Restarts the loop", "is_correct": False},
                    {"text": "Raises an exception", "is_correct": False},
                ]
            },
            {
                "text": "Which keyword is used to define a function in Python?",
                "choices": [
                    {"text": "def", "is_correct": True},
                    {"text": "function", "is_correct": False},
                    {"text": "func", "is_correct": False},
                    {"text": "define", "is_correct": False},
                ]
            },
        ]
    },
    "Object-Oriented Programming": {
        "passing_score": 70,
        "description": "Test your knowledge of OOP concepts in Python including classes, inheritance, and polymorphism.",
        "questions": [
            {
                "text": "What is the correct way to define a class in Python?",
                "choices": [
                    {"text": "class MyClass:", "is_correct": True},
                    {"text": "class MyClass():", "is_correct": False},
                    {"text": "new MyClass:", "is_correct": False},
                    {"text": "define MyClass:", "is_correct": False},
                ]
            },
            {
                "text": "What does `super()` do in Python?",
                "choices": [
                    {"text": "Calls the parent class method", "is_correct": True},
                    {"text": "Creates a new instance", "is_correct": False},
                    {"text": "Deletes an instance", "is_correct": False},
                    {"text": "Returns the class name", "is_correct": False},
                ]
            },
            {
                "text": "Which of the following is NOT a pillar of OOP?",
                "choices": [
                    {"text": "Compilation", "is_correct": True},
                    {"text": "Inheritance", "is_correct": False},
                    {"text": "Polymorphism", "is_correct": False},
                    {"text": "Encapsulation", "is_correct": False},
                ]
            },
        ]
    },
    "Real-World Projects": {
        "passing_score": 70,
        "description": "Test your understanding of building real-world Python projects.",
        "questions": [
            {
                "text": "Which library is commonly used for web scraping in Python?",
                "choices": [
                    {"text": "BeautifulSoup", "is_correct": True},
                    {"text": "Django", "is_correct": False},
                    {"text": "Flask", "is_correct": False},
                    {"text": "NumPy", "is_correct": False},
                ]
            },
            {
                "text": "What module is used to create CLI tools with argument parsing?",
                "choices": [
                    {"text": "argparse", "is_correct": True},
                    {"text": "sys", "is_correct": False},
                    {"text": "os", "is_correct": False},
                    {"text": "json", "is_correct": False},
                ]
            },
            {
                "text": "Which HTTP method is used to create a new resource in a REST API?",
                "choices": [
                    {"text": "POST", "is_correct": True},
                    {"text": "GET", "is_correct": False},
                    {"text": "DELETE", "is_correct": False},
                    {"text": "PUT", "is_correct": False},
                ]
            },
        ]
    },
    "React Fundamentals": {
        "passing_score": 70,
        "description": "Test your knowledge of React basics including components, props, and hooks.",
        "questions": [
            {
                "text": "What is the correct way to pass data from a parent to a child component in React?",
                "choices": [
                    {"text": "Props", "is_correct": True},
                    {"text": "State", "is_correct": False},
                    {"text": "Context", "is_correct": False},
                    {"text": "Refs", "is_correct": False},
                ]
            },
            {
                "text": "Which hook is used to manage state in a functional component?",
                "choices": [
                    {"text": "useState", "is_correct": True},
                    {"text": "useEffect", "is_correct": False},
                    {"text": "useContext", "is_correct": False},
                    {"text": "useRef", "is_correct": False},
                ]
            },
            {
                "text": "What is the purpose of the `useEffect` hook?",
                "choices": [
                    {"text": "Run side effects after render", "is_correct": True},
                    {"text": "Create a new component", "is_correct": False},
                    {"text": "Define CSS styles", "is_correct": False},
                    {"text": "Handle form validation", "is_correct": False},
                ]
            },
            {
                "text": "What does the Context API help avoid?",
                "choices": [
                    {"text": "Prop drilling", "is_correct": True},
                    {"text": "Component re-renders", "is_correct": False},
                    {"text": "State management", "is_correct": False},
                    {"text": "Code splitting", "is_correct": False},
                ]
            },
        ]
    },
    "Django REST Framework": {
        "passing_score": 70,
        "description": "Test your understanding of Django REST Framework models, serializers, and views.",
        "questions": [
            {
                "text": "What is a serializer in DRF used for?",
                "choices": [
                    {"text": "Converting complex data to/from JSON", "is_correct": True},
                    {"text": "Creating database tables", "is_correct": False},
                    {"text": "Managing user sessions", "is_correct": False},
                    {"text": "Compiling static files", "is_correct": False},
                ]
            },
            {
                "text": "Which DRF view provides GET, POST, PUT, PATCH, and DELETE for a model?",
                "choices": [
                    {"text": "ModelViewSet", "is_correct": True},
                    {"text": "APIView", "is_correct": False},
                    {"text": "ListCreateAPIView", "is_correct": False},
                    {"text": "ViewSet", "is_correct": False},
                ]
            },
            {
                "text": "What does `IsAuthenticated` permission class do?",
                "choices": [
                    {"text": "Allows access only to logged-in users", "is_correct": True},
                    {"text": "Allows access to admin users only", "is_correct": False},
                    {"text": "Allows access to everyone", "is_correct": False},
                    {"text": "Allows access based on IP address", "is_correct": False},
                ]
            },
        ]
    },
    "Integration & Deployment": {
        "passing_score": 70,
        "description": "Test your knowledge of full-stack integration and deployment.",
        "questions": [
            {
                "text": "What is CORS used for in web development?",
                "choices": [
                    {"text": "Allowing cross-origin requests", "is_correct": True},
                    {"text": "Encrypting database connections", "is_correct": False},
                    {"text": "Minimising JavaScript bundles", "is_correct": False},
                    {"text": "Creating API endpoints", "is_correct": False},
                ]
            },
            {
                "text": "What does Docker containerisation provide?",
                "choices": [
                    {"text": "Consistent environments across machines", "is_correct": True},
                    {"text": "Automatic database scaling", "is_correct": False},
                    {"text": "Built-in authentication", "is_correct": False},
                    {"text": "Real-time WebSocket support", "is_correct": False},
                ]
            },
            {
                "text": "What is the purpose of CI/CD pipelines?",
                "choices": [
                    {"text": "Automate build, test, and deployment", "is_correct": True},
                    {"text": "Create user interfaces", "is_correct": False},
                    {"text": "Manage database migrations", "is_correct": False},
                    {"text": "Generate documentation", "is_correct": False},
                ]
            },
        ]
    },
    "Design Thinking": {
        "passing_score": 70,
        "description": "Test your knowledge of the design thinking process.",
        "questions": [
            {
                "text": "What is the first stage of the Design Thinking process?",
                "choices": [
                    {"text": "Empathise", "is_correct": True},
                    {"text": "Ideate", "is_correct": False},
                    {"text": "Prototype", "is_correct": False},
                    {"text": "Test", "is_correct": False},
                ]
            },
            {
                "text": "What is a problem statement in the Define phase?",
                "choices": [
                    {"text": "A clear articulation of the user's need", "is_correct": True},
                    {"text": "A list of technical requirements", "is_correct": False},
                    {"text": "A budget estimate", "is_correct": False},
                    {"text": "A marketing plan", "is_correct": False},
                ]
            },
            {
                "text": "What is the main goal of prototyping?",
                "choices": [
                    {"text": "Learn and iterate quickly", "is_correct": True},
                    {"text": "Create a production-ready product", "is_correct": False},
                    {"text": "Write production code", "is_correct": False},
                    {"text": "Finalise the design", "is_correct": False},
                ]
            },
            {
                "text": "How many users are recommended for usability testing per round?",
                "choices": [
                    {"text": "5", "is_correct": True},
                    {"text": "50", "is_correct": False},
                    {"text": "100", "is_correct": False},
                    {"text": "1", "is_correct": False},
                ]
            },
        ]
    },
    "Figma Mastery": {
        "passing_score": 70,
        "description": "Test your Figma skills including components, auto layout, and prototyping.",
        "questions": [
            {
                "text": "What keyboard shortcut creates a frame in Figma?",
                "choices": [
                    {"text": "F", "is_correct": True},
                    {"text": "R", "is_correct": False},
                    {"text": "T", "is_correct": False},
                    {"text": "A", "is_correct": False},
                ]
            },
            {
                "text": "What is Auto Layout in Figma similar to in CSS?",
                "choices": [
                    {"text": "Flexbox", "is_correct": True},
                    {"text": "Grid", "is_correct": False},
                    {"text": "Position absolute", "is_correct": False},
                    {"text": "Float", "is_correct": False},
                ]
            },
            {
                "text": "What is the purpose of component variants in Figma?",
                "choices": [
                    {"text": "Group related component states", "is_correct": True},
                    {"text": "Create colour palettes", "is_correct": False},
                    {"text": "Add animation to prototypes", "is_correct": False},
                    {"text": "Export assets", "is_correct": False},
                ]
            },
        ]
    },
    "ML Foundations": {
        "passing_score": 70,
        "description": "Test your understanding of machine learning fundamentals.",
        "questions": [
            {
                "text": "What is the goal of linear regression?",
                "choices": [
                    {"text": "Model relationship between variables", "is_correct": True},
                    {"text": "Classify data into categories", "is_correct": False},
                    {"text": "Cluster similar data points", "is_correct": False},
                    {"text": "Reduce dimensionality", "is_correct": False},
                ]
            },
            {
                "text": "Which metric is best for imbalanced classification problems?",
                "choices": [
                    {"text": "F1-Score", "is_correct": True},
                    {"text": "Accuracy", "is_correct": False},
                    {"text": "Mean Squared Error", "is_correct": False},
                    {"text": "R-squared", "is_correct": False},
                ]
            },
            {
                "text": "What does cross-validation help prevent?",
                "choices": [
                    {"text": "Overfitting", "is_correct": True},
                    {"text": "Underfitting", "is_correct": False},
                    {"text": "Gradient explosion", "is_correct": False},
                    {"text": "Memory leaks", "is_correct": False},
                ]
            },
            {
                "text": "What is feature engineering?",
                "choices": [
                    {"text": "Transforming raw data into better features", "is_correct": True},
                    {"text": "Selecting the best algorithm", "is_correct": False},
                    {"text": "Tuning hyperparameters", "is_correct": False},
                    {"text": "Deploying the model", "is_correct": False},
                ]
            },
        ]
    },
    "Deep Learning": {
        "passing_score": 70,
        "description": "Test your knowledge of neural networks and deep learning.",
        "questions": [
            {
                "text": "What activation function is commonly used in hidden layers?",
                "choices": [
                    {"text": "ReLU", "is_correct": True},
                    {"text": "Softmax", "is_correct": False},
                    {"text": "Linear", "is_correct": False},
                    {"text": "Step function", "is_correct": False},
                ]
            },
            {
                "text": "What is transfer learning?",
                "choices": [
                    {"text": "Using a pre-trained model on a new task", "is_correct": True},
                    {"text": "Training a model from scratch", "is_correct": False},
                    {"text": "Transferring data between databases", "is_correct": False},
                    {"text": "Copying model weights to a new file", "is_correct": False},
                ]
            },
            {
                "text": "What type of neural network is best for image classification?",
                "choices": [
                    {"text": "CNN", "is_correct": True},
                    {"text": "RNN", "is_correct": False},
                    {"text": "LSTM", "is_correct": False},
                    {"text": "GAN", "is_correct": False},
                ]
            },
        ]
    },
    "NLP & Deployment": {
        "passing_score": 70,
        "description": "Test your understanding of NLP and ML model deployment.",
        "questions": [
            {
                "text": "What does TF-IDF stand for in text processing?",
                "choices": [
                    {"text": "Term Frequency-Inverse Document Frequency", "is_correct": True},
                    {"text": "Text Format-Integrated Data Format", "is_correct": False},
                    {"text": "Total Feature-Inverse Distribution Function", "is_correct": False},
                    {"text": "Token Frequency-Indexed Document Format", "is_correct": False},
                ]
            },
            {
                "text": "What key innovation do Transformers introduce?",
                "choices": [
                    {"text": "Self-attention mechanism", "is_correct": True},
                    {"text": "Backpropagation", "is_correct": False},
                    {"text": "Convolutional layers", "is_correct": False},
                    {"text": "Recurrent connections", "is_correct": False},
                ]
            },
            {
                "text": "Which framework is recommended for serving ML models as APIs?",
                "choices": [
                    {"text": "FastAPI", "is_correct": True},
                    {"text": "Django Templates", "is_correct": False},
                    {"text": "Flask (without REST)", "is_correct": False},
                    {"text": "Streamlit", "is_correct": False},
                ]
            },
        ]
    },
    "Foundations of Strategy": {
        "passing_score": 70,
        "description": "Test your knowledge of business strategy frameworks.",
        "questions": [
            {
                "text": "What are the five forces in Porter's Five Forces model?",
                "choices": [
                    {"text": "Rivalry, new entrants, substitutes, supplier power, buyer power", "is_correct": True},
                    {"text": "Price, product, promotion, place, people", "is_correct": False},
                    {"text": "Strengths, weaknesses, opportunities, threats, trends", "is_correct": False},
                    {"text": "Vision, mission, strategy, tactics, execution", "is_correct": False},
                ]
            },
            {
                "text": "How many building blocks are in the Business Model Canvas?",
                "choices": [
                    {"text": "9", "is_correct": True},
                    {"text": "5", "is_correct": False},
                    {"text": "7", "is_correct": False},
                    {"text": "12", "is_correct": False},
                ]
            },
            {
                "text": "What does the 'O' in SWOT stand for?",
                "choices": [
                    {"text": "Opportunities", "is_correct": True},
                    {"text": "Operations", "is_correct": False},
                    {"text": "Objectives", "is_correct": False},
                    {"text": "Organisation", "is_correct": False},
                ]
            },
        ]
    },
    "Building & Scaling": {
        "passing_score": 70,
        "description": "Test your understanding of startup building and scaling.",
        "questions": [
            {
                "text": "What is product-market fit?",
                "choices": [
                    {"text": "When a product satisfies strong market demand", "is_correct": True},
                    {"text": "When a product is fully developed", "is_correct": False},
                    {"text": "When a company goes public", "is_correct": False},
                    {"text": "When a product is priced correctly", "is_correct": False},
                ]
            },
            {
                "text": "What stage of fundraising typically follows a seed round?",
                "choices": [
                    {"text": "Series A", "is_correct": True},
                    {"text": "Series B", "is_correct": False},
                    {"text": "Series C", "is_correct": False},
                    {"text": "IPO", "is_correct": False},
                ]
            },
            {
                "text": "What is a growth hacking mindset primarily focused on?",
                "choices": [
                    {"text": "Experimenting to find effective growth methods", "is_correct": True},
                    {"text": "Hiring the best marketers", "is_correct": False},
                    {"text": "Spending more on advertising", "is_correct": False},
                    {"text": "Copying competitor strategies", "is_correct": False},
                ]
            },
        ]
    },
    "Camera Fundamentals": {
        "passing_score": 70,
        "description": "Test your understanding of camera basics including exposure, aperture, and ISO.",
        "questions": [
            {
                "text": "What three settings make up the exposure triangle?",
                "choices": [
                    {"text": "Aperture, shutter speed, ISO", "is_correct": True},
                    {"text": "Aperture, focal length, ISO", "is_correct": False},
                    {"text": "Shutter speed, white balance, ISO", "is_correct": False},
                    {"text": "Focus, aperture, shutter speed", "is_correct": False},
                ]
            },
            {
                "text": "A wider aperture (lower f-number) results in:",
                "choices": [
                    {"text": "Shallower depth of field", "is_correct": True},
                    {"text": "Deeper depth of field", "is_correct": False},
                    {"text": "Less light entering the lens", "is_correct": False},
                    {"text": "Slower shutter speed required", "is_correct": False},
                ]
            },
            {
                "text": "What is the reciprocal rule for handholding a camera?",
                "choices": [
                    {"text": "Shutter speed should be at least 1/focal length", "is_correct": True},
                    {"text": "Aperture should match focal length", "is_correct": False},
                    {"text": "ISO should be set to 100", "is_correct": False},
                    {"text": "Shutter speed should be 1 second", "is_correct": False},
                ]
            },
            {
                "text": "Higher ISO settings result in:",
                "choices": [
                    {"text": "More image noise", "is_correct": True},
                    {"text": "Less image noise", "is_correct": False},
                    {"text": "Shallower depth of field", "is_correct": False},
                    {"text": "Faster autofocus", "is_correct": False},
                ]
            },
        ]
    },
    "Composition & Lighting": {
        "passing_score": 70,
        "description": "Test your knowledge of composition techniques and lighting.",
        "questions": [
            {
                "text": "What does the rule of thirds help create?",
                "choices": [
                    {"text": "More dynamic compositions", "is_correct": True},
                    {"text": "Perfect exposure", "is_correct": False},
                    {"text": "Sharp focus", "is_correct": False},
                    {"text": "Accurate colours", "is_correct": False},
                ]
            },
            {
                "text": "When is the golden hour for photography?",
                "choices": [
                    {"text": "Shortly after sunrise and before sunset", "is_correct": True},
                    {"text": "Midday when the sun is highest", "is_correct": False},
                    {"text": "During a solar eclipse", "is_correct": False},
                    {"text": "At midnight under a full moon", "is_correct": False},
                ]
            },
            {
                "text": "What is a key light in studio photography?",
                "choices": [
                    {"text": "The main light source", "is_correct": True},
                    {"text": "The light behind the subject", "is_correct": False},
                    {"text": "A small accent light", "is_correct": False},
                    {"text": "Background illumination", "is_correct": False},
                ]
            },
        ]
    },
    "Post-Processing": {
        "passing_score": 70,
        "description": "Test your understanding of photo editing workflows.",
        "questions": [
            {
                "text": "Which editing adjustment controls the darkest parts of an image?",
                "choices": [
                    {"text": "Shadows", "is_correct": True},
                    {"text": "Highlights", "is_correct": False},
                    {"text": "Whites", "is_correct": False},
                    {"text": "Exposure", "is_correct": False},
                ]
            },
            {
                "text": "What colour space is recommended for web export?",
                "choices": [
                    {"text": "sRGB", "is_correct": True},
                    {"text": "Adobe RGB", "is_correct": False},
                    {"text": "CMYK", "is_correct": False},
                    {"text": "ProPhoto RGB", "is_correct": False},
                ]
            },
            {
                "text": "What is frequency separation used for?",
                "choices": [
                    {"text": "Skin retouching while preserving texture", "is_correct": True},
                    {"text": "Increasing image resolution", "is_correct": False},
                    {"text": "Removing lens distortion", "is_correct": False},
                    {"text": "Converting to black and white", "is_correct": False},
                ]
            },
        ]
    },
    "Data Manipulation": {
        "passing_score": 70,
        "description": "Test your knowledge of data manipulation with Pandas.",
        "questions": [
            {
                "text": "Which Pandas method is used to read a CSV file?",
                "choices": [
                    {"text": "pd.read_csv()", "is_correct": True},
                    {"text": "pd.load_csv()", "is_correct": False},
                    {"text": "pd.import_csv()", "is_correct": False},
                    {"text": "pd.open_csv()", "is_correct": False},
                ]
            },
            {
                "text": "What does `df.isnull().sum()` do?",
                "choices": [
                    {"text": "Counts missing values per column", "is_correct": True},
                    {"text": "Sums all numeric columns", "is_correct": False},
                    {"text": "Removes all null values", "is_correct": False},
                    {"text": "Creates a summary statistics table", "is_correct": False},
                ]
            },
            {
                "text": "Which method combines two DataFrames on a common column?",
                "choices": [
                    {"text": "pd.merge()", "is_correct": True},
                    {"text": "pd.concat()", "is_correct": False},
                    {"text": "pd.join()", "is_correct": False},
                    {"text": "pd.combine()", "is_correct": False},
                ]
            },
            {
                "text": "How do you resample time series data to monthly frequency?",
                "choices": [
                    {"text": "df.resample('M').mean()", "is_correct": True},
                    {"text": "df.monthly().mean()", "is_correct": False},
                    {"text": "df.groupby('month').mean()", "is_correct": False},
                    {"text": "df.rolling('M').mean()", "is_correct": False},
                ]
            },
        ]
    },
    "Visualization": {
        "passing_score": 70,
        "description": "Test your knowledge of data visualisation libraries.",
        "questions": [
            {
                "text": "Which library is built on top of Matplotlib for statistical visualisations?",
                "choices": [
                    {"text": "Seaborn", "is_correct": True},
                    {"text": "Plotly", "is_correct": False},
                    {"text": "Bokeh", "is_correct": False},
                    {"text": "ggplot", "is_correct": False},
                ]
            },
            {
                "text": "Which library creates interactive web-based charts?",
                "choices": [
                    {"text": "Plotly", "is_correct": True},
                    {"text": "Matplotlib", "is_correct": False},
                    {"text": "Seaborn", "is_correct": False},
                    {"text": "Pandas", "is_correct": False},
                ]
            },
            {
                "text": "What Python library is used to build data dashboards?",
                "choices": [
                    {"text": "Streamlit", "is_correct": True},
                    {"text": "FastAPI", "is_correct": False},
                    {"text": "Flask", "is_correct": False},
                    {"text": "Django", "is_correct": False},
                ]
            },
        ]
    },
    "SEO Fundamentals": {
        "passing_score": 70,
        "description": "Test your knowledge of SEO basics including keywords and on-page optimisation.",
        "questions": [
            {
                "text": "What is a long-tail keyword?",
                "choices": [
                    {"text": "A very specific, longer search phrase", "is_correct": True},
                    {"text": "A highly competitive keyword", "is_correct": False},
                    {"text": "A keyword with high search volume", "is_correct": False},
                    {"text": "A brand name keyword", "is_correct": False},
                ]
            },
            {
                "text": "Where should the primary keyword ideally appear in a page?",
                "choices": [
                    {"text": "Title tag, H1, first 100 words", "is_correct": True},
                    {"text": "Only in the meta description", "is_correct": False},
                    {"text": "Only in image alt text", "is_correct": False},
                    {"text": "In the URL only", "is_correct": False},
                ]
            },
            {
                "text": "What is link building in SEO?",
                "choices": [
                    {"text": "Acquiring hyperlinks from other websites", "is_correct": True},
                    {"text": "Creating internal links between pages", "is_correct": False},
                    {"text": "Building a website navigation menu", "is_correct": False},
                    {"text": "Creating social media profiles", "is_correct": False},
                ]
            },
            {
                "text": "What does a technical SEO audit check?",
                "choices": [
                    {"text": "Crawlability, indexability, page speed, mobile-friendliness", "is_correct": True},
                    {"text": "Keyword rankings and search volume", "is_correct": False},
                    {"text": "Social media engagement metrics", "is_correct": False},
                    {"text": "Email open rates", "is_correct": False},
                ]
            },
        ]
    },
    "Paid Advertising": {
        "passing_score": 70,
        "description": "Test your knowledge of paid advertising on Google and Meta.",
        "questions": [
            {
                "text": "What does ROAS stand for in advertising?",
                "choices": [
                    {"text": "Return on Ad Spend", "is_correct": True},
                    {"text": "Revenue of Advertising Sales", "is_correct": False},
                    {"text": "Rate of Audience Saturation", "is_correct": False},
                    {"text": "Return on Audience Segmentation", "is_correct": False},
                ]
            },
            {
                "text": "Which Meta Ads targeting type finds users similar to your best customers?",
                "choices": [
                    {"text": "Lookalike audiences", "is_correct": True},
                    {"text": "Custom audiences", "is_correct": False},
                    {"text": "Interest targeting", "is_correct": False},
                    {"text": "Demographic targeting", "is_correct": False},
                ]
            },
            {
                "text": "What is retargeting?",
                "choices": [
                    {"text": "Showing ads to people who visited your site", "is_correct": True},
                    {"text": "A/B testing different ad creatives", "is_correct": False},
                    {"text": "Optimising ad delivery schedules", "is_correct": False},
                    {"text": "Expanding to new audiences", "is_correct": False},
                ]
            },
        ]
    },
    "Content & Email": {
        "passing_score": 70,
        "description": "Test your knowledge of content marketing and email sequences.",
        "questions": [
            {
                "text": "What does AIDA stand for in copywriting?",
                "choices": [
                    {"text": "Attention, Interest, Desire, Action", "is_correct": True},
                    {"text": "Analyse, Ideate, Develop, Assess", "is_correct": False},
                    {"text": "Awareness, Interest, Decision, Action", "is_correct": False},
                    {"text": "Attract, Inform, Delight, Activate", "is_correct": False},
                ]
            },
            {
                "text": "What is the recommended time interval for a welcome email sequence?",
                "choices": [
                    {"text": "Multiple emails over several days", "is_correct": True},
                    {"text": "One email only", "is_correct": False},
                    {"text": "An email every hour", "is_correct": False},
                    {"text": "An email once a month", "is_correct": False},
                ]
            },
            {
                "text": "What does GA4 use as its primary data model?",
                "choices": [
                    {"text": "Events", "is_correct": True},
                    {"text": "Page views", "is_correct": False},
                    {"text": "Sessions", "is_correct": False},
                    {"text": "Transactions", "is_correct": False},
                ]
            },
        ]
    },
    "Advanced Patterns": {
        "passing_score": 70,
        "description": "Test your knowledge of advanced React patterns.",
        "questions": [
            {
                "text": "What pattern uses a function as a prop to control rendering?",
                "choices": [
                    {"text": "Render props", "is_correct": True},
                    {"text": "Compound components", "is_correct": False},
                    {"text": "Higher-order components", "is_correct": False},
                    {"text": "Custom hooks", "is_correct": False},
                ]
            },
            {
                "text": "What is a Higher-Order Component?",
                "choices": [
                    {"text": "A function that takes a component and returns a new one", "is_correct": True},
                    {"text": "A component with more props than usual", "is_correct": False},
                    {"text": "A component that renders HTML elements", "is_correct": False},
                    {"text": "A class component with lifecycle methods", "is_correct": False},
                ]
            },
            {
                "text": "What naming convention must custom hooks follow?",
                "choices": [
                    {"text": "Start with 'use'", "is_correct": True},
                    {"text": "Start with 'hook'", "is_correct": False},
                    {"text": "End with 'Hook'", "is_correct": False},
                    {"text": "Be all lowercase", "is_correct": False},
                ]
            },
        ]
    },
    "Performance": {
        "passing_score": 70,
        "description": "Test your knowledge of React performance optimisation.",
        "questions": [
            {
                "text": "What does React.memo do?",
                "choices": [
                    {"text": "Prevents re-renders when props haven't changed", "is_correct": True},
                    {"text": "Increases the rendering speed", "is_correct": False},
                    {"text": "Creates a memo of the component state", "is_correct": False},
                    {"text": "Optimises network requests", "is_correct": False},
                ]
            },
            {
                "text": "What technique divides your bundle into smaller chunks?",
                "choices": [
                    {"text": "Code splitting", "is_correct": True},
                    {"text": "Tree shaking", "is_correct": False},
                    {"text": "Minification", "is_correct": False},
                    {"text": "Caching", "is_correct": False},
                ]
            },
            {
                "text": "What does virtualization help with in React?",
                "choices": [
                    {"text": "Rendering large lists efficiently", "is_correct": True},
                    {"text": "Virtual DOM diffing", "is_correct": False},
                    {"text": "Creating virtual network connections", "is_correct": False},
                    {"text": "Simulating user interactions", "is_correct": False},
                ]
            },
        ]
    },
    "State Management": {
        "passing_score": 70,
        "description": "Test your knowledge of React state management solutions.",
        "questions": [
            {
                "text": "What problem does splitting Contexts solve?",
                "choices": [
                    {"text": "Excessive re-renders of all consumers", "is_correct": True},
                    {"text": "Slow import times", "is_correct": False},
                    {"text": "Large bundle size", "is_correct": False},
                    {"text": "Prop drilling", "is_correct": False},
                ]
            },
            {
                "text": "What is Zustand primarily known for?",
                "choices": [
                    {"text": "Simple, minimal state management without boilerplate", "is_correct": True},
                    {"text": "Complex reducer patterns", "is_correct": False},
                    {"text": "Server-side rendering", "is_correct": False},
                    {"text": "GraphQL integration", "is_correct": False},
                ]
            },
            {
                "text": "What does React Query specialise in?",
                "choices": [
                    {"text": "Server state management with caching", "is_correct": True},
                    {"text": "Form state management", "is_correct": False},
                    {"text": "URL routing", "is_correct": False},
                    {"text": "CSS-in-JS styling", "is_correct": False},
                ]
            },
        ]
    },
    "Brand Strategy": {
        "passing_score": 70,
        "description": "Test your knowledge of brand strategy fundamentals.",
        "questions": [
            {
                "text": "What is the goal of a brand discovery workshop?",
                "choices": [
                    {"text": "Understand the business, audience, and competitive landscape", "is_correct": True},
                    {"text": "Design the final logo", "is_correct": False},
                    {"text": "Build the website", "is_correct": False},
                    {"text": "Write marketing copy", "is_correct": False},
                ]
            },
            {
                "text": "What is brand positioning?",
                "choices": [
                    {"text": "How you want your brand to be perceived vs competitors", "is_correct": True},
                    {"text": "The price point of your products", "is_correct": False},
                    {"text": "The location of your stores", "is_correct": False},
                    {"text": "The design of your logo", "is_correct": False},
                ]
            },
            {
                "text": "What is the purpose of a moodboard?",
                "choices": [
                    {"text": "Capture the visual direction of a brand", "is_correct": True},
                    {"text": "Present final logo designs", "is_correct": False},
                    {"text": "Track project deadlines", "is_correct": False},
                    {"text": "Budget for design costs", "is_correct": False},
                ]
            },
        ]
    },
    "Visual Identity": {
        "passing_score": 70,
        "description": "Test your knowledge of visual identity design.",
        "questions": [
            {
                "text": "What type of logo is the Nike swoosh?",
                "choices": [
                    {"text": "Abstract", "is_correct": True},
                    {"text": "Wordmark", "is_correct": False},
                    {"text": "Lettermark", "is_correct": False},
                    {"text": "Emblem", "is_correct": False},
                ]
            },
            {
                "text": "What colour is associated with trust and calm?",
                "choices": [
                    {"text": "Blue", "is_correct": True},
                    {"text": "Red", "is_correct": False},
                    {"text": "Green", "is_correct": False},
                    {"text": "Purple", "is_correct": False},
                ]
            },
            {
                "text": "What is the recommended maximum number of typefaces in a brand system?",
                "choices": [
                    {"text": "2-3", "is_correct": True},
                    {"text": "5-6", "is_correct": False},
                    {"text": "8-10", "is_correct": False},
                    {"text": "1", "is_correct": False},
                ]
            },
        ]
    },
    "Style Guide Creation": {
        "passing_score": 70,
        "description": "Test your knowledge of creating brand style guides.",
        "questions": [
            {
                "text": "What is the main purpose of brand guidelines?",
                "choices": [
                    {"text": "Ensure brand consistency across all channels", "is_correct": True},
                    {"text": "Increase social media followers", "is_correct": False},
                    {"text": "Reduce design costs", "is_correct": False},
                    {"text": "Sell design services", "is_correct": False},
                ]
            },
            {
                "text": "What should be included in a brand guidelines document?",
                "choices": [
                    {"text": "Logo usage, colour palette, typography, voice and tone", "is_correct": True},
                    {"text": "Only the logo variations", "is_correct": False},
                    {"text": "Employee handbook policies", "is_correct": False},
                    {"text": "Product pricing strategy", "is_correct": False},
                ]
            },
            {
                "text": "What is the first step in a brand rollout?",
                "choices": [
                    {"text": "Internal launch and employee training", "is_correct": True},
                    {"text": "Updating the website", "is_correct": False},
                    {"text": "Printing new business cards", "is_correct": False},
                    {"text": "Running launch advertisements", "is_correct": False},
                ]
            },
        ]
    },
    "VC Fundamentals": {
        "passing_score": 70,
        "description": "Test your knowledge of venture capital fundamentals.",
        "questions": [
            {
                "text": "What is carried interest in a VC fund?",
                "choices": [
                    {"text": "The GP's share of profits (typically 20%)", "is_correct": True},
                    {"text": "The annual management fee", "is_correct": False},
                    {"text": "Interest paid to LPs on their capital", "is_correct": False},
                    {"text": "A loan to the startup", "is_correct": False},
                ]
            },
            {
                "text": "What is deal sourcing in venture capital?",
                "choices": [
                    {"text": "Identifying and evaluating potential investments", "is_correct": True},
                    {"text": "Negotiating the final contract", "is_correct": False},
                    {"text": "Selling portfolio company shares", "is_correct": False},
                    {"text": "Hiring new investment analysts", "is_correct": False},
                ]
            },
            {
                "text": "What does a cap table show?",
                "choices": [
                    {"text": "Who owns what in a company", "is_correct": True},
                    {"text": "The company's revenue cap", "is_correct": False},
                    {"text": "Maximum market capitalisation", "is_correct": False},
                    {"text": "Salary cap for executives", "is_correct": False},
                ]
            },
        ]
    },
    "Valuation & Terms": {
        "passing_score": 70,
        "description": "Test your understanding of startup valuation and term sheets.",
        "questions": [
            {
                "text": "If a company has a $10M pre-money valuation and raises $2M, what is the post-money valuation?",
                "choices": [
                    {"text": "$12M", "is_correct": True},
                    {"text": "$10M", "is_correct": False},
                    {"text": "$8M", "is_correct": False},
                    {"text": "$20M", "is_correct": False},
                ]
            },
            {
                "text": "What is a SAFE in startup financing?",
                "choices": [
                    {"text": "Simple Agreement for Future Equity", "is_correct": True},
                    {"text": "Standard Annual Funding Estimate", "is_correct": False},
                    {"text": "Secured Asset Financing Entity", "is_correct": False},
                    {"text": "Strategic Advance for Enterprise", "is_correct": False},
                ]
            },
            {
                "text": "What does a liquidation preference determine?",
                "choices": [
                    {"text": "Who gets paid first in an exit", "is_correct": True},
                    {"text": "The company's liquidation value", "is_correct": False},
                    {"text": "The maximum funding amount", "is_correct": False},
                    {"text": "The interest rate on debt", "is_correct": False},
                ]
            },
        ]
    },
    "Planning & Field Craft": {
        "passing_score": 70,
        "description": "Test your knowledge of landscape photography planning.",
        "questions": [
            {
                "text": "What are the best times of day for landscape photography?",
                "choices": [
                    {"text": "Golden hour and blue hour", "is_correct": True},
                    {"text": "Midday when the sun is highest", "is_correct": False},
                    {"text": "Only during sunrise", "is_correct": False},
                    {"text": "Only at night", "is_correct": False},
                ]
            },
            {
                "text": "What tool is essential for planning landscape photo shoots?",
                "choices": [
                    {"text": "Weather and light prediction apps", "is_correct": True},
                    {"text": "A GPS for driving directions", "is_correct": False},
                    {"text": "A light meter", "is_correct": False},
                    {"text": "A colour calibration card", "is_correct": False},
                ]
            },
            {
                "text": "What is location scouting in landscape photography?",
                "choices": [
                    {"text": "Visiting and evaluating potential shooting locations", "is_correct": True},
                    {"text": "Scouting for wildlife in the area", "is_correct": False},
                    {"text": "Checking weather conditions", "is_correct": False},
                    {"text": "Finding the nearest parking", "is_correct": False},
                ]
            },
        ]
    },
    "Techniques": {
        "passing_score": 70,
        "description": "Test your knowledge of advanced landscape photography techniques.",
        "questions": [
            {
                "text": "What is long exposure photography used for?",
                "choices": [
                    {"text": "Smoothing water and clouds", "is_correct": True},
                    {"text": "Freezing fast action", "is_correct": False},
                    {"text": "Reducing image noise", "is_correct": False},
                    {"text": "Increasing colour saturation", "is_correct": False},
                ]
            },
            {
                "text": "What is the purpose of ND filters?",
                "choices": [
                    {"text": "Reduce light entering the lens for longer exposures", "is_correct": True},
                    {"text": "Add colour effects to images", "is_correct": False},
                    {"text": "Protect the lens from scratches", "is_correct": False},
                    {"text": "Increase sharpness", "is_correct": False},
                ]
            },
            {
                "text": "What is focus stacking?",
                "choices": [
                    {"text": "Combining multiple shots with different focus points", "is_correct": True},
                    {"text": "Using multiple camera bodies simultaneously", "is_correct": False},
                    {"text": "Stacking filters on the lens", "is_correct": False},
                    {"text": "Arranging multiple subjects in the frame", "is_correct": False},
                ]
            },
        ]
    },
    "Techniques and Post-Processing": {
        "passing_score": 70,
        "description": "Test your knowledge of landscape post-processing.",
        "questions": [
            {
                "text": "What is the benefit of shooting in RAW format?",
                "choices": [
                    {"text": "More flexibility in post-processing", "is_correct": True},
                    {"text": "Smaller file sizes", "is_correct": False},
                    {"text": "Faster shooting speed", "is_correct": False},
                    {"text": "Built-in noise reduction", "is_correct": False},
                ]
            },
            {
                "text": "What is dodging and burning in photo editing?",
                "choices": [
                    {"text": "Selectively lightening and darkening areas", "is_correct": True},
                    {"text": "Removing dust spots from the sensor", "is_correct": False},
                    {"text": "Adjusting white balance", "is_correct": False},
                    {"text": "Cropping the image", "is_correct": False},
                ]
            },
            {
                "text": "What is sky replacement in landscape editing?",
                "choices": [
                    {"text": "Replacing the sky with a different one", "is_correct": True},
                    {"text": "Adjusting the colour of the sky", "is_correct": False},
                    {"text": "Removing clouds from the sky", "is_correct": False},
                    {"text": "Adding stars to the sky", "is_correct": False},
                ]
            },
        ]
    },
}


class Command(BaseCommand):
    help = "Generate rich content for all lessons and create quizzes for all modules."

    def handle(self, *args, **options):
        self._add_content_to_lessons()
        self._create_quizzes()

    def _add_content_to_lessons(self):
        updated = 0
        typed = 0
        for lesson in Lesson.objects.select_related("module__course").all():
            content = generate_content(
                lesson.title,
                lesson.module.title,
                lesson.module.course.title
            )
            if content:
                lesson.content = content
                lesson.lesson_type = get_lesson_type(lesson.title)
                lesson.save(update_fields=["content", "lesson_type"])
                updated += 1
                if lesson.lesson_type == "PDF":
                    typed += 1

        self.stdout.write(
            self.style.SUCCESS(f"Updated {updated} lessons with rich content")
        )
        self.stdout.write(
            self.style.SUCCESS(f"  Set {typed} lessons to PDF type")
        )

    def _create_quizzes(self):
        created = 0
        skipped = 0
        for module in Module.objects.all():
            template = QUIZ_TEMPLATES.get(module.title)
            if not template:
                # Try matching a fallback key
                for key in QUIZ_TEMPLATES:
                    if any(word in module.title.lower() for word in key.lower().split()):
                        template = QUIZ_TEMPLATES[key]
                        break
                if not template:
                    self.stdout.write(
                        self.style.WARNING(f"  No quiz template for module: {module.title}")
                    )
                    skipped += 1
                    continue

            if Quiz.objects.filter(module=module).exists():
                self.stdout.write(f"  Quiz already exists for: {module.title}")
                skipped += 1
                continue

            quiz = Quiz.objects.create(
                module=module,
                title=f"{module.title} Quiz",
                description=template.get("description", f"Test your knowledge of {module.title}."),
                passing_score=template.get("passing_score", 70),
            )

            for i, q_data in enumerate(template["questions"]):
                question = QuizQuestion.objects.create(
                    quiz=quiz,
                    text=q_data["text"],
                    order=i + 1,
                )
                for c_data in q_data["choices"]:
                    QuizChoice.objects.create(
                        question=question,
                        text=c_data["text"],
                        is_correct=c_data["is_correct"],
                    )

            created += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Created quiz: {quiz.title} "
                    f"({len(template['questions'])} questions)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f"Created {created} quizzes")
        )
        if skipped:
            self.stdout.write(
                self.style.WARNING(f"Skipped {skipped} modules (template not found or quiz exists)")
            )
