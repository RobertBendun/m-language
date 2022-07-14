# M Language

Small experiment in writing stack-based concatenative programming language with pattern matching without thinking about good pattern matching algorithm and doing this whole thing in about an hour.

Example factorial implementation, that prints `120`:

```
: n factorial = n 1 - factorial n * ;
: 0 factorial = 1 ;

5 factorial print
```

## Language description

The main abstraction of the language are definitions - procedures with pattern matching.
Example definition that does nothing when called is `: nop = ;`.

`:` introduces definition, `=` separates body from arguments and `;` ends the definition.

Language supports also:

- numeric literals, which pushes value onto the stack like `10`
- arithmetic operations: `+`, `-`, `*` which takes 2 values from the stack and calculates result based on type of operation witch is put back onto stack
- print with `print`, that prints top of the stack

Classical stack manipulation operations can be defined using definitions:

- `: _ drop = ;` removes top of the stack
- `: a dup = a a ;` replicates top of the stack
- `: a b swap = b a ;` swaps elements on top of the stack
- `: a b over = a b a ;` brings element from one before top to the top of the stack

## What could be added?

The main thing that would improve langauge would be **quotations**. They will alow for user defined if statements:

```
: if-false _        0 if = if-false ;
: _        if-true  _ if = if-true  ;

[ 42 print ] [ 7 print ] 1 if
```

prints `7`. They well known feature in languages like [Factor](https://factorcode.org/)
