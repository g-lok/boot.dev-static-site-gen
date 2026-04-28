import unittest

from textnode import BlockType, TextNode, TextType
from texthelpers import (
    split_nodes_delimiter,
    extract_markdown_links,
    extract_markdown_images,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_text_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a  node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_type_not_eq(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_url_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD, url="https://google.com")
        node2 = TextNode("This is a text node", TextType.BOLD, url="https://yahoo.com")
        self.assertNotEqual(node, node2)

    def test_no_url(self):
        node = TextNode("This is a text node", TextType.BOLD, url="https://google.com")
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_to_html_plain(self):
        node = TextNode("This is plaintext", TextType.TEXT)
        html_node = node.to_html_node()
        self.assertEqual(str(html_node), "LeafNode(None, This is plaintext, None)")
        html_str = html_node.to_html()
        self.assertEqual(html_str, "This is plaintext")

    def test_to_html_bold(self):
        node = TextNode("This is bold", TextType.BOLD)
        html_node = node.to_html_node()
        self.assertEqual(str(html_node), "LeafNode(b, This is bold, None)")
        html_str = html_node.to_html()
        self.assertEqual(html_str, "<b>This is bold</b>")

    def test_to_html_italic(self):
        node = TextNode("This is italic", TextType.ITALIC)
        html_node = node.to_html_node()
        self.assertEqual(str(html_node), "LeafNode(i, This is italic, None)")
        html_str = html_node.to_html()
        self.assertEqual(html_str, "<i>This is italic</i>")

    def test_to_html_code(self):
        node = TextNode("This is code", TextType.CODE)
        html_node = node.to_html_node()
        self.assertEqual(str(html_node), "LeafNode(code, This is code, None)")
        html_str = html_node.to_html()
        self.assertEqual(html_str, "<code>This is code</code>")

    def test_to_html_link(self):
        node = TextNode("This is link", TextType.LINK, url="https://yahoo.com")
        html_node = node.to_html_node()
        self.assertEqual(
            str(html_node), "LeafNode(a, This is link, {'href': 'https://yahoo.com'})"
        )
        html_str = html_node.to_html()
        self.assertEqual(html_str, '<a href="https://yahoo.com">This is link</a>')

    def test_to_html_image(self):
        node = TextNode(
            "This is an image", TextType.IMAGE, url="https://yahoo.com/logo.png"
        )
        html_node = node.to_html_node()
        self.assertEqual(
            str(html_node),
            "LeafNode(img, , {'src': 'https://yahoo.com/logo.png', 'alt': 'This is an image'})",
        )
        html_str = html_node.to_html()
        self.assertEqual(
            html_str,
            '<img src="https://yahoo.com/logo.png" alt="This is an image"></img>',
        )

    def test_split_delimit_single(self):
        node1 = TextNode("this is plain", TextType.TEXT)
        node2 = TextNode("this is _italic_ text", TextType.TEXT)
        node3 = TextNode("this is *italic* text", TextType.TEXT)
        node4 = TextNode("this is __bold__ text", TextType.TEXT)
        node5 = TextNode("this is **bold** text", TextType.TEXT)
        node6 = TextNode("this is `code` text", TextType.TEXT)
        node7 = TextNode("this is ``code`` text", TextType.TEXT)
        nodes = [node1, node2, node3, node4, node5, node6, node7]
        splitted = split_nodes_delimiter(nodes)

        expected = [
            TextNode("this is plain", TextType.TEXT),
            TextNode("this is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
            TextNode("this is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
            TextNode("this is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
            TextNode("this is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
            TextNode("this is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
            TextNode("this is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(splitted, expected)

    def test_split_delimit_multiple(self):
        node1 = TextNode("this is plain", TextType.TEXT)
        node2 = TextNode("this is _italic_ **bold** `code` text", TextType.TEXT)
        nodes = [node1, node2]
        splitted = split_nodes_delimiter(nodes)

        expected = [
            TextNode("this is plain", TextType.TEXT),
            TextNode("this is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(splitted, expected)

    def test_split_delimit_escp_backtick(self):
        node1 = TextNode("This is ``escaped `backticks` `` text", TextType.TEXT)
        nodes = [node1]
        splitted = split_nodes_delimiter(nodes)

        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("escaped `backticks` ", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(splitted, expected)

    def test_split_delimit_nested(self):
        with self.assertRaises(ValueError) as context:
            node1 = TextNode("This is _nested **text**_", TextType.TEXT)
            nodes = [node1]
            splitted = split_nodes_delimiter(nodes)
        self.assertEqual(
            str(context.exception), "Nested inline delimiters not yet supported"
        )

    def test_split_delimit_unclosed(self):
        with self.assertRaises(ValueError) as context:
            node1 = TextNode("This is **unclosed text", TextType.TEXT)
            nodes = [node1]
            splitted = split_nodes_delimiter(nodes)
        self.assertEqual(str(context.exception), "'**' delimiter not closed")

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with an [link](https://google.com)"
        )
        self.assertListEqual([("link", "https://google.com")], matches)

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with an [google link](https://www.google.com) and another [second link](https://www.yahoo.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("google link", TextType.LINK, "https://www.google.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://www.yahoo.com"),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_md_to_block_types(self):
        md = """
# This is a header

## This is a second header

```
This is
a code
block
```

> this
>is
> a quote

- this is
- an
- unordered
- list

1. This
2. is
3. an ordered
4. list

This is a
regular
paragraph
"""
        blocks = markdown_to_blocks(md)
        btypes = []
        for block in blocks:
            btypes.append(markdown_to_blocks(block))
        self.assertEqual(
            btypes,
            [
                BlockType.HEADING,
                BlockType.HEADING,
                BlockType.CODE,
                BlockType.QUOTE,
                BlockType.UNORDERED_LIST,
                BlockType.ORDERED_LIST,
                BlockType.PARAGRAPH,
            ],
        )


if __name__ == "__main__":
    unittest.main()
