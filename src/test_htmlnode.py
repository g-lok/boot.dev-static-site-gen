import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode
from texthelpers import markdown_to_html_node


class TestHTMLNode(unittest.TestCase):
    def test_eq_tag_val(self):
        node = HTMLNode("p", "this is a paragraph")
        node2 = HTMLNode("p", "this is a paragraph")
        self.assertEqual(node, node2)

    def test_not_eq_tag(self):
        node = HTMLNode("a", "this is a paragraph")
        node2 = HTMLNode("p", "this is a paragraph")
        self.assertNotEqual(node, node2)

    # def test_no_val_no_children(self):
    #     with self.assertRaises(ValueError) as context:
    #         node = HTMLNode("p")
    #     self.assertEqual(
    #         str(context.exception), "HTMLNode must have either value or children"
    #     )

    def test_val_and_children(self):
        with self.assertRaises(ValueError) as context:
            childnode = HTMLNode("p", "paragraph2")
            node = HTMLNode("p", "paragraph", [childnode])
        self.assertEqual(
            str(context.exception), "HTMLNode cannot have both value and children"
        )

    def test_props(self):
        node = HTMLNode(
            "a",
            "something",
            props={"href": "https://www.google.com", "target": "_blank"},
        )
        props_str = node.props_to_html()
        self.assertEqual(props_str, ' href="https://www.google.com" target="_blank"')

    def test_no_props(self):
        node = HTMLNode(
            "a",
            "something",
        )
        props_str = node.props_to_html()
        self.assertEqual(props_str, "")

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "This is a link", props={"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">This is a link</a>'
        )

    def test_leaf_no_tag(self):
        node = LeafNode(
            value="This is not a link", props={"href": "https://www.google.com"}
        )
        self.assertEqual(node.to_html(), "This is not a link")

    def test_leaf_no_val(self):
        with self.assertRaises(ValueError) as context:
            leafnode = LeafNode("p")
            html_str = leafnode.to_html()
        self.assertEqual(str(context.exception), "LeafNode must have value")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_grandchildren_props(self):
        grandchild_node = LeafNode(
            "a", "grandchild", props={"href": "https://www.google.com"}
        )
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            '<div><span><a href="https://www.google.com">grandchild</a></span></div>',
        )

    def test_parent_no_tag(self):
        with self.assertRaises(ValueError) as context:
            child_node = LeafNode("span", "child")
            parent_node = ParentNode(children=[child_node])
            html_str = parent_node.to_html()
        self.assertEqual(str(context.exception), "ParentNode must have a tag")

    def test_parent_no_children(self):
        with self.assertRaises(ValueError) as context:
            parent_node = ParentNode("b")
            html_str = parent_node.to_html()
        self.assertEqual(str(context.exception), "ParentNode must have children")

        def test_paragraphs(self):
            md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

            node = markdown_to_html_node(md)
            html = node.to_html()
            print(html)
            self.assertEqual(
                html,
                "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
            )

        def test_codeblock(self):
            md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

            node = markdown_to_html_node(md)
            html = node.to_html()
            self.assertEqual(
                html,
                "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
            )

    def test_quoteblock(self):
        md = """
This is a **regular** paragraph

> this _is_ a
> quoted
> block
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            r"<div><p>This is a <b>regular</b> paragraph</p><blockquote>this <i>is</i> aquotedblock</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
This is a **regular** paragraph

- this **is**
- an `unordered`
- _list_
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            r"<div><p>This is a <b>regular</b> paragraph</p><ul><li>this <b>is</b></li><li>an <code>unordered</code></li><li><i>list</i></li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
This is a **regular** paragraph

1. this **is**
2. an `ordered`
3. _list_
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            r"<div><p>This is a <b>regular</b> paragraph</p><ol><li>this <b>is</b></li><li>an <code>ordered</code></li><li><i>list</i></li></ol></div>",
        )


if __name__ == "__main__":
    unittest.main()
