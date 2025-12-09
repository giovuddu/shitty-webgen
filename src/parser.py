import re
from textnode import TextNode, TextType


def split_node_delimiter(
    old_node: TextNode, delimiter: str, text_type: TextType
) -> list[TextNode]:
    nodes = []
    sp = old_node.text.split(delimiter, 1)

    if len(sp) <= 1:
        if not old_node.text:
            return []
        return [old_node]

    nodes.append(TextNode(sp[0], TextType.TEXT))
    rest = sp[1]

    rest_sp = rest.split(delimiter, 1)

    if len(rest_sp) <= 1:
        raise Exception(f"unmatched delimiter found in {old_node.text}")

    nodes.append(TextNode(rest_sp[0], text_type))
    right = TextNode(rest_sp[1], TextType.TEXT)

    return [
        node for node in nodes if node.text_type != TextType.TEXT or node.text
    ] + split_node_delimiter(right, delimiter, text_type)


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    res = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            res += split_node_delimiter(node, delimiter, text_type)
        else:
            res += [node]

    return res


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?<!!)\[(.*?)\]\((.*?)\)", text)


def split_node_image_link(node: TextNode, image: bool) -> list[TextNode]:
    nodes = []
    cur = node
    if image:
        metas = extract_markdown_images(node.text)
    else:
        metas = extract_markdown_links(node.text)

    for meta in metas:
        if image:
            rest = cur.text.split(f"![{meta[0]}]({meta[1]})")
        else:
            rest = cur.text.split(f"[{meta[0]}]({meta[1]})")

        nodes.append(TextNode(rest[0], TextType.TEXT))
        if image:
            nodes.append(TextNode(meta[0], TextType.IMAGE, meta[1]))
        else:
            nodes.append(TextNode(meta[0], TextType.LINK, meta[1]))
        right = TextNode(rest[1], TextType.TEXT)

        cur = right
    nodes.append(cur)

    return [node for node in nodes if node.text_type != TextType.TEXT or node.text]


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    res = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            res += split_node_image_link(node, True)
        else:
            res += [node]

    return res


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    res = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            res += split_node_image_link(node, False)
        else:
            res += [node]

    return res
