from dataclasses import dataclass, field
from copy import copy
import operator
import argparse

interpreter_arguments = argparse.ArgumentParser(
    description="M Language interpreter")
interpreter_arguments.add_argument(
    'source', help="Path to M file that should be interpreted")

args = interpreter_arguments.parse_args()

with open(args.source) as f:
    source = f.read()

# We simply split tokens according to whitespace.
# All tokens that are not whitespace are valid langauge identifiers
tokens = source.split()


@dataclass
class Definition:
    "Holds information about definitions introduced in user code"

    params: list[str] = field(default_factory=list)
    body: list[str] = field(default_factory=list)


# List of definitions from source code
definitions: list[Definition] = []

# Current stack during execution
stack = []


def param_equal(parameter: str, argument: int):
    """
    Returns if paramters can be subsituted for each other

    Identifier can always be matched with integer argument,
    but numeric paramter only can be matched with argument
    that holds the same value
    """
    if parameter.isdigit():
        return argument == int(parameter)
    return True


def run_candidate(candidate: Definition):
    "Runs given definition, substituting its parameters inside body"
    global stack
    body = copy(candidate.body)
    args_len = len(candidate.params) - 1
    args, stack = stack[-args_len:], stack[:-args_len]
    params = candidate.params[:-1]

    for token in body:
        try:
            idx = params.index(token)
            stack.append(args[idx])
            continue
        except ValueError:
            pass
        run(token)


# List of builtin operations, that are predefined for the user
builtins = [
    [2, True,  '-',     operator.sub],
    [2, True,  '*',     operator.mul],
    [2, True,  '+',     operator.add],
    [1, False, 'print', lambda x: print(x)],
]


def run(token: str):
    "Runs given token resolving builtins, numeric literals and definitions"
    global stack

    if token.isdigit():
        stack.append(int(token))
        return

    for arity, keep_result, expected, resolver in builtins:
        if expected == token:
            if arity > len(stack):
                print("Missing %d arguments on the stack for operation %s" %
                      (arity - len(stack), token))
                exit(1)
            args, stack = stack[-arity:], stack[:-arity]
            result = resolver(*args)
            if keep_result:
                if isinstance(result, (list, tuple)):
                    stack.extend(result)
                else:
                    stack.append(result)
            return

    candidates = [
        definition for definition in definitions
        if definition.params[-1] == token
        if len(definition.params)-1 <= len(stack)
        if all(param_equal(definition.params[:-1][i], stack[i])
               for i in range(len(definition.params)-1))
    ]

    if not candidates:
        print(f"Cannot resolve given token '{token}'")
        exit(1)

    if len(candidates) == 1:
        run_candidate(candidates[0])
        return

    assert all(len(candidate.params)
               for candidate in candidates), "Different arity of definitions is not allowed"

    args_len = len(candidates[0].params)-1
    for i in range(args_len):
        has_concrete_param = [
            j for j, candidate in enumerate(candidates)
            if candidate.params[i].isdigit() and int(candidate.params[i]) == stack[-args_len + i]
        ]
        if len(has_concrete_param) != 0:
            candidates = [candidates[j] for j in has_concrete_param]

    if len(candidates) == 1:
        run_candidate(candidates[0])
        return

    print(f"{candidates=}")
    assert False, "Unknown token type in run: " + token


# Definition that is currently beeing defined
current_definition = None

# If we are inside parameter or body part of definiton
inside_body = False

# Execute all top level code including definining definitions
for token in tokens:
    if token == ':':
        assert current_definition is None, "Definitions cannot be nested"
        current_definition = Definition()
        inside_body = False
    elif current_definition:
        if inside_body:
            if token == ';':
                definitions.append(current_definition)
                current_definition = None
            else:
                current_definition.body.append(token)
        else:
            if token == '=':
                inside_body = True
            else:
                current_definition.params.append(token)
    else:
        run(token)
