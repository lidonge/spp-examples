#!/usr/bin/env python3
"""Format demo source-language files without changing their lexical tokens."""
from pathlib import Path
import argparse
import re


TOKEN = re.compile(
    r'(?P<space>\s+)|(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|'
    r'(?P<string>"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')|'
    r'(?P<word>[\w]+)|(?P<operator>\+\+|--|\+=|-=|\*=|/=|==|!=|>=|<=|&&|\|\||->)|'
    r'(?P<punct>[^\s])'
)


def tokens(text):
    return [(m.lastgroup, m.group()) for m in TOKEN.finditer(text) if m.lastgroup != 'space']


def wrap_arguments(line, width=110):
    """Use Java-style continuation indentation for long comma-separated arguments."""
    if len(line) <= width:
        return [line]
    depth = 0
    opening = closing = None
    commas = []
    for match in TOKEN.finditer(line):
        token = match.group()
        if match.lastgroup in {'string', 'comment', 'space'}:
            continue
        if token == '(':
            if depth == 0:
                opening = match.start()
            depth += 1
        elif token == ')':
            if depth == 0:
                continue
            depth -= 1
            if depth == 0 and opening is not None:
                closing = match.start()
                break
        elif token == ',' and depth == 1:
            commas.append(match.start())
    if opening is None or closing is None or not commas:
        return [line]
    indent = line[:len(line) - len(line.lstrip())]
    result = [line[:opening + 1]]
    start = opening + 1
    for comma in commas:
        result.append(indent + '    ' + line[start:comma + 1].strip())
        start = comma + 1
    result.append(indent + '    ' + line[start:closing].strip())
    result.append(indent + line[closing:])
    return [wrapped for part in result for wrapped in wrap_arguments(part, width)]


def wrap_expression(line, width=110):
    """Break long expressions at binary operators, preserving all tokens."""
    if len(line) <= width:
        return [line]
    cuts = []
    previous = None
    for match in TOKEN.finditer(line):
        if match.lastgroup in {'space', 'comment'}:
            continue
        value = match.group()
        if value in {'&&', '||'} or (
            value in {'+', '-', '*', '/'} and previous is not None
            and (previous.lastgroup in {'word', 'string'} or previous.group() in {')', ']'})
        ):
            cuts.append(match.start())
        previous = match
    if not cuts:
        return [line]
    indent = line[:len(line) - len(line.lstrip())] + '    '
    pieces = [line[:cuts[0]].rstrip()]
    for start, end in zip(cuts, cuts[1:] + [len(line)]):
        pieces.append(indent + line[start:end].strip())
    return pieces


def format_source(text):
    matches = list(TOKEN.finditer(text))
    output, buffer, stack = [], '', []
    parentheses = 0
    previous_end = 0
    line_indent = None
    case_label = False

    def indentation():
        return len(stack) + sum(frame['case'] for frame in stack)

    def append(token, gap=' '):
        nonlocal buffer, line_indent
        if not buffer:
            line_indent = indentation()
        if buffer and gap:
            buffer += ' '
        buffer += token

    def flush():
        nonlocal buffer, line_indent
        if buffer.strip():
            output.append('    ' * line_indent + buffer.strip())
        buffer, line_indent = '', None

    def blank():
        if output and output[-1] and not output[-1].endswith(('{', ':')):
            output.append('')

    significant = [(i, m) for i, m in enumerate(matches) if m.lastgroup != 'space']
    for position, (index, match) in enumerate(significant):
        token = match.group()
        gap = text[previous_end:match.start()]
        previous_end = match.end()
        following = significant[position + 1][1].group() if position + 1 < len(significant) else ''
        if match.lastgroup == 'comment':
            flush()
            # Preserve inline comments on the source statement they annotate.
            if token.startswith('//') and '\n' not in gap and output and output[-1]:
                output[-1] += ' ' + token
            else:
                for part in token.splitlines():
                    output.append('    ' * indentation() + part)
            continue
        if not buffer and gap.count('\n') > 1:
            blank()
        if not buffer and not stack and parentheses == 0 and token in {'atomic', 'Scenario', 'Entity', 'Role', 'Contract', 'take', 'Reference', 'Enum'}:
            blank()
        if token in {'case', 'default'} and parentheses == 0 and stack and stack[-1]['kind'] == 'switch':
            flush()
            stack[-1]['case'] = False
            case_label = True
        if token == '{':
            heading = buffer.strip()
            kind = 'switch' if heading.startswith('switch') else 'enum' if heading.startswith('Enum ') else 'initializer' if '=' in heading and 'new ' in heading else 'block'
            append('{', ' ')
            flush()
            stack.append({'kind': kind, 'case': False})
        elif token == '}':
            flush()
            while output and not output[-1]:
                output.pop()
            if not stack:
                raise ValueError('Unmatched closing brace')
            stack.pop()
            append('}', '')
            if following not in {';', ',', ')', 'else', 'fail'}:
                flush()
                if not stack:
                    blank()
        elif token == ';':
            append(';', '')
            if parentheses == 0:
                flush()
                if not stack and output[-1].startswith('domain '):
                    blank()
        elif token == ',' and parentheses == 0 and stack and stack[-1]['kind'] in {'enum', 'initializer'}:
            append(',', '')
            flush()
        elif token == ':' and case_label and parentheses == 0:
            append(':', '')
            flush()
            stack[-1]['case'] = True
            case_label = False
        else:
            if token == '(':
                parentheses += 1
                if buffer.strip() in {'if', 'for', 'while', 'switch'}:
                    gap = ' '
            elif token == ')':
                parentheses -= 1
            append(token, gap)
    flush()
    if stack or parentheses:
        raise ValueError('Unbalanced source delimiters')
    result = '\n'.join(
        expression
        for original in output
        for line in wrap_arguments(original)
        for expression in wrap_expression(line)
    ).rstrip() + '\n'
    if tokens(result) != tokens(text):
        raise ValueError('Formatting changed source tokens')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='report files requiring formatting without editing')
    parser.add_argument('paths', type=Path, nargs='*')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parent.parent
    roots = args.paths or [repo / demo / 'src/main/spp' for demo in ['demos/petstore', 'demos/bank-deposit']]
    files = sorted({p for root in roots for p in ([root] if root.is_file() else root.rglob('*')) if p.suffix in {'.spp', '.app', '.phy', '.enum'}})
    changed = 0
    for path in files:
        original = path.read_text()
        formatted = format_source(original)
        if format_source(formatted) != formatted:
            raise ValueError(f'Formatter is not stable for {path}')
        if formatted != original:
            changed += 1
            if not args.check:
                path.write_text(formatted)
    print(f'{len(files)} files checked; {changed} {"need formatting" if args.check else "formatted"}; lexical tokens unchanged.')
    if args.check and changed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
