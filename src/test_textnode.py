import unittest

from textnode import TextNode, TextType
from htmlnode import LeafNode


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
        node = TextNode("This is plaintext", TextType.PLAIN)
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


if __name__ == "__main__":
    unittest.main()
