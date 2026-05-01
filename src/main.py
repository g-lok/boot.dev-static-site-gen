import re
import os
import shutil

import jinja2

# from textnode import TextType, TextNode
from texthelpers import markdown_to_html_node


def get_static_public_abs_path():
    content_dirs = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(script_dir)
    content_dirs["static"] = os.path.join(script_dir, "..", "static/")
    content_dirs["public"] = os.path.join(script_dir, "..", "public/")
    content_dirs["content"] = os.path.join(script_dir, "..", "content/")
    content_dirs["template"] = os.path.join(script_dir, "..", "template.html")
    return content_dirs


def clear_public_dir(public_dir):
    deleted_files = []
    deleted_dirs = []
    for root, dirs, files in os.walk(public_dir, topdown=False):
        for name in files:
            deleted_files.append(os.path.join(root, name))
            os.remove(os.path.join(root, name))
        for name in dirs:
            deleted_dirs.append(os.path.join(root, name))
            shutil.rmtree(os.path.join(root, name))
    return {"deleted_files": deleted_files, "deleted_dirs": deleted_dirs}


def cp_static_to_public(static_dir, public_dir):
    cp_files = []
    for root, dirs, files in os.walk(static_dir):
        # Calculate the relative path to maintain structure
        relative_path = os.path.relpath(root, static_dir)
        target_dir = os.path.join(public_dir, relative_path)

        # Create directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)

        # Copy each file
        for file in files:
            static_dir_file = os.path.join(root, file)
            public_dir_file = os.path.join(target_dir, file)
            cp_files.append(public_dir_file)
            shutil.copy2(static_dir_file, public_dir_file)
    return cp_files


def extract_title(markdown):
    lines = markdown.split("\n")
    pattern = r"(^\#{1,6}) (.*)"
    for line in lines:
        matches = re.findall(pattern, line)
        h_num = f"h{len(matches[0][0])}"
        text = matches[0][1]
        if h_num == "h1":
            return text
    raise ValueError("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path):
    print(
        f"Generating page from {from_path} to {dest_path} using template {template_path}"
    )

    with open(from_path, "r") as f:
        md = f.read()

    with open(template_path, "r") as f:
        template = f.read()

    htmlnode = markdown_to_html_node(md)
    html = htmlnode.to_html()
    title = extract_title(md)
    environment = jinja2.Environment()
    template = environment.from_string(template)
    rendered = template.render(Title=title, Content=html)

    dir_path = os.path.dirname(dest_path)
    os.makedirs(dir_path, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(rendered)

    print("Page generated")


def generate_pages_recursive(content_dir, template_path, public_dir):
    for root, dirs, files in os.walk(content_dir):
        # Calculate the relative path to maintain structure
        relative_path = os.path.relpath(root, content_dir)
        target_dir = os.path.join(public_dir, relative_path)

        # Create directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)

        # Copy each file
        for file in files:
            content_dir_file = os.path.join(root, file)
            public_dir_file = os.path.join(target_dir, file.replace(".md", ".html"))
            generate_page(content_dir_file, template_path, public_dir_file)


def main():
    content_dirs = get_static_public_abs_path()
    deleted = clear_public_dir(content_dirs["public"])
    print("Deleted: ", deleted)
    files = cp_static_to_public(content_dirs["static"], content_dirs["public"])
    print("Copied", files)
    # indexmd = os.path.join(content_dirs["content"], "index.md")
    # indexhtml = os.path.join(content_dirs["public"], "index.html")
    generate_pages_recursive(
        content_dirs["content"], content_dirs["template"], content_dirs["public"]
    )


if __name__ == "__main__":
    main()
