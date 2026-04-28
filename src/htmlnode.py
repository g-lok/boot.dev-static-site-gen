class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

        # if self.value is None and self.children is None:
        #     raise ValueError("HTMLNode must have either value or children")

        if self.value is not None and self.children is not None:
            raise ValueError("HTMLNode cannot have both value and children")

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props is None:
            return ""
        if not isinstance(self.props, dict):
            raise TypeError("props must be type dict[str, str]")

        rtn_str = ""
        for k, v in self.props.items():
            rtn_str += f' {k}="{v}"'
        return rtn_str

    def __eq__(self, other) -> bool:
        return (
            self.tag == other.tag
            and self.value == other.value
            and self.children == other.children
            and self.props == other.props
        )

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, props=None):
        super().__init__(tag, value, children=None, props=props)

    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have value")
        if self.tag is None:
            return self.value
        rtn_str = f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
        return rtn_str

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(self, tag=None, children=None, props=None):
        super().__init__(tag, value=None, children=children, props=props)

    def to_html(self):
        if self.children is None:
            raise ValueError("ParentNode must have children")
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        inner_str = ""
        for child in self.children:
            inner_str += child.to_html()
        rtn_str = f"<{self.tag}{self.props_to_html()}>{inner_str}</{self.tag}>"
        return rtn_str

    def __repr__(self):
        return f"ParentNode({self.tag}, {self.children}, {self.props})"
