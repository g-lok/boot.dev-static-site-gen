from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextType, BlockType, TextNode
import re

import textnode


def extract_markdown_images(text):
    pattern = r"\!\[(.*?)\]\((.*?)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"\[(.*?)\]\((.*?)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        # Capturing groups here ensure the link components stay in the split list
        parts = re.split(r"(\[.*?\]\(.*?\))", original_text)

        for part in parts:
            if part == "":
                continue

            # Check if the part is a markdown link
            link_match = re.match(r"\[(.*?)\]\((.*?)\)", part)
            if link_match:
                link_text = link_match.group(1)
                link_url = link_match.group(2)
                new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            else:
                # It's just normal text
                new_nodes.append(TextNode(part, TextType.TEXT))

    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        original_text = old_node.text
        # Capturing groups here ensure the image components stay in the split list
        parts = re.split(r"(\!\[.*?\]\(.*?\))", original_text)

        for part in parts:
            if part == "":
                continue

            # Check if the part is a markdown image
            link_match = re.match(r"\!\[(.*?)\]\((.*?)\)", part)
            if link_match:
                alt_text = link_match.group(1)
                image_url = link_match.group(2)
                new_nodes.append(TextNode(alt_text, TextType.IMAGE, image_url))
            else:
                # It's just normal text
                new_nodes.append(TextNode(part, TextType.TEXT))

    return new_nodes


def split_nodes_delimiter(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        delimiters = ["__", "__"]  # For bold
        delimiters += ["**", "**"]  # For bold
        delimiters += ["``", "``"]  # For code required escaped backticks
        delimiters += ["_", "_"]  # For italic
        delimiters += ["*", "*"]  # For italic
        delimiters += ["`", "`"]  # For code
        pattern = "|".join(f"({re.escape(d)})" for d in delimiters)
        result = re.split(pattern, node.text)
        result = [part for part in result if part]  # filter empty strings

        open_block = None
        block_text = ""
        for part in result:
            if part not in delimiters and open_block is None:
                node = TextNode(part, TextType.TEXT)
                new_nodes.append(node)
                continue
            if part in delimiters and open_block is None:
                open_block = part
                continue
            if part in delimiters and open_block is not None:
                if part == open_block:
                    match part:
                        case "_" | "*":
                            node = TextNode(block_text, TextType.ITALIC)
                            new_nodes.append(node)
                            block_text = ""
                            open_block = None
                            continue
                        case "__" | "**":
                            node = TextNode(block_text, TextType.BOLD)
                            new_nodes.append(node)
                            block_text = ""
                            open_block = None
                            continue
                        case "`" | "``":
                            node = TextNode(block_text, TextType.CODE)
                            new_nodes.append(node)
                            block_text = ""
                            open_block = None
                            continue
                elif open_block == "``" and part == "`":
                    block_text += part
                    continue
                else:
                    raise ValueError("Nested inline delimiters not yet supported")
            if part not in delimiters and open_block is not None:
                block_text += part
        if block_text:
            raise ValueError(f"'{open_block}' delimiter not closed")

    return new_nodes


def text_to_textnodes(text):
    node = TextNode(text, TextType.TEXT)
    highlighted_nodes = split_nodes_delimiter([node])
    nodes_w_images = split_nodes_image(highlighted_nodes)
    nodes_complete = split_nodes_link(nodes_w_images)
    return nodes_complete


def markdown_to_blocks(markdown):
    split = [block.strip() for block in markdown.split("\n\n") if block.strip()]
    return split


def block_to_block_type(block):
    block_patterns = {
        r"(^\#{1,6} {1}.*)": BlockType.HEADING,
        r"(^`{3}\n[\s\S]*?\n`{3}$)": BlockType.CODE,
        r"(^\>.*)": BlockType.QUOTE,
        r"(^- {1}.*)": BlockType.UNORDERED_LIST,
        r"(^\d+. {1}.*)": BlockType.ORDERED_LIST,
    }
    for pattern, btype in block_patterns.items():
        matches = re.findall(pattern, block)
        if matches:
            if btype in (BlockType.HEADING, BlockType.CODE):
                return btype
            if btype in (BlockType.QUOTE, BlockType.UNORDERED_LIST):
                lines = block.split("\n")
                matches = []
                for line in lines:
                    match = re.findall(pattern, line)
                    matches.append(match)
                if all(matches):
                    return btype
                else:
                    if btype == BlockType.QUOTE:
                        raise ValueError("All lines in quote block must start with '>'")
                    else:
                        raise ValueError(
                            "All lines in an unordered list block must start with '- '"
                        )
            else:
                lines = block.split("\n")
                last_num = 0
                for line in lines:
                    match = re.findall(pattern, line)
                    if not match:
                        raise ValueError(
                            "All lines in ordered list block must begin with '[int]. "
                        )
                    num = int(re.findall(r"(^\d+)", line)[0])
                    if num != last_num + 1:
                        raise ValueError(
                            "Line numbers in ordered list must be sequential"
                        )
                    last_num = num
                return btype

    return BlockType.PARAGRAPH


def text_to_children(tag, text):
    textnodes = text_to_textnodes(text)
    htmlnodes = []
    for node in textnodes:
        htmlnodes.append(node.to_html_node())
    return ParentNode(tag, children=htmlnodes)


def block_header_to_html_node(block):
    # might need to parse other inline markdown
    pattern = r"(^\#{1,6}) (.*$)"
    matches = re.findall(pattern, block)
    h_num = f"h{len(matches[0][0])}"
    text = matches[0][1]
    return text_to_children(h_num, text)


def block_code_to_html_node(block):
    pattern = r"(^`{3}\n)([\s\S\n]*)(`{3}$)"
    matches = re.findall(pattern, block)
    text = matches[0][1]
    return ParentNode("pre", [LeafNode("code", text)])


def block_quote_to_html_node(block):
    lines = block.split("\n")
    children = []
    for line in lines:
        stripped = line.strip("> ").strip(">")
        textnodes = text_to_textnodes(stripped)
        for node in textnodes:
            children.append(node.to_html_node())
    return ParentNode("blockquote", children)


def block_uord_list_to_html_node(block):
    children = []
    pattern = r"(^- {1})(.*)"
    lines = block.split("\n")
    for line in lines:
        if not line:
            continue
        matches = re.findall(pattern, line)
        text = matches[0][1]
        line_nodes = text_to_children("li", text)
        children.append(line_nodes)
    return ParentNode("ul", children=children)


def block_ord_list_to_html_node(block):
    children = []
    pattern = r"(^\d+. {1})(.*)"
    lines = block.split("\n")
    for line in lines:
        if not line:
            continue
        matches = re.findall(pattern, line)
        text = matches[0][1]
        line_nodes = text_to_children("li", text)
        children.append(line_nodes)
    return ParentNode("ol", children=children)


def block_paragraph_to_html_node(block):
    children = []
    lines = block.split("\n")
    for line in lines:
        if not line:
            continue
        children.append(text_to_children("p", line.strip()))
    return ParentNode("p", children=children)


def markdown_to_html_node(md):
    children = []
    blocks = markdown_to_blocks(md)
    blocks_types = [(block, block_to_block_type(block)) for block in blocks]
    for block, btype in blocks_types:
        match btype:
            case BlockType.HEADING:
                children.append(block_header_to_html_node(block))
            case BlockType.CODE:
                children.append(block_code_to_html_node(block))
            case BlockType.QUOTE:
                children.append(block_quote_to_html_node(block))
            case BlockType.UNORDERED_LIST:
                children.append(block_uord_list_to_html_node(block))
            case BlockType.ORDERED_LIST:
                children.append(block_ord_list_to_html_node(block))
            case BlockType.PARAGRAPH:
                children.append(
                    text_to_children(
                        "p", " ".join(block.strip().replace("\n", " ").split())
                    )
                )
    return ParentNode("div", children=children)
