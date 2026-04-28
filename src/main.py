from textnode import TextType, TextNode


def main():
    text_obj = TextNode("this is text", TextType.BOLD)
    print(text_obj)


if __name__ == "__main__":
    main()
