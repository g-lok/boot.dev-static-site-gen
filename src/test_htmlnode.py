import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


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


if __name__ == "__main__":
    unittest.main()
