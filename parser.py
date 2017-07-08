import re
import lib.base_token as base_token
import lib.block_token as block_token
import lib.leaf_token as leaf_token
from lib.reader import *

def tokenize(lines):
    tokens = []
    index = 0
    while index < len(lines):
        if lines[index].startswith('#'):
            tokens.append(block_token.Heading(lines[index]))
            index += 1
        elif lines[index].startswith('> '):
            end_index = read_quote(index, lines)
            tokens.append(block_token.Quote(lines[index:end_index]))
            index = end_index
        elif lines[index].startswith('```'):
            end_index = read_block_code(index, lines)
            tokens.append(block_token.BlockCode(lines[index:end_index]))
            index = end_index
        elif lines[index] == '---\n':
            tokens.append(block_token.Separator)
            index += 1
        elif lines[index].startswith('- '):
            end_index = read_list(index, lines)
            tokens.append(build_list(lines[index:end_index]))
            index = end_index
        elif lines[index] == '\n':
            index += 1
        else:
            end_index = read_paragraph(index, lines)
            tokens.append(block_token.Paragraph(lines[index:end_index]))
            index = end_index
    return tokens

def tokenize_inner(content):
    tokens = []

    def append_token(token_type, content, index):
        tokens.append(token_type(content[:index]))
        tokenize_inner_helper(content[index:])

    def tokenize_inner_helper(content):
        if content == '':                                 # base case
            return
        if re.match(r"\*\*(.+?)\*\*", content):           # bold
            i = content.index('**', 1) + 2
            append_token(leaf_token.Bold, content, i)
        elif re.match(r"\*(.+?)\*", content):             # italics
            i = content.index('*', 1) + 1
            append_token(leaf_token.Italic, content, i)
        elif re.match(r"`(.+?)`", content):               # inline code
            i = content.index('`', 1) + 1
            append_token(leaf_token.InlineCode, content, i)
        elif re.match(r"\[(.+?)\]\((.+?)\)", content):    # link
            i = content.index(')') + 1
            append_token(leaf_token.Link, content, i)
        else:                                             # raw text
            try:                      # next token
                p = r"(`(.+?)`)|(\*\*(.+?)\*\*)|(\*(.+?)\*)|\[(.+?)\]\((.+?)\)"
                i = re.search(p, content).start()
            except AttributeError:    # no more tokens
                i = len(content)
            append_token(leaf_token.RawText, content, i)
    tokenize_inner_helper(content)
    return tokens

def build_list(lines, level=0):
    l = block_token.List()
    index = 0
    while index < len(lines):
        if lines[index][level*4:].startswith('- '):
            l.add(block_token.ListItem(lines[index]))
        else:
            curr_level = level + 1
            end_index = read_list(index, lines, curr_level)
            l.add(build_list(lines[index:end_index], curr_level))
            index = end_index - 1
        index += 1
    return l
