from textnode import TextNode, TextType


def split_node_delimiter(
    old_node: TextNode, delimiter: str, text_type: TextType
) -> list[TextNode]:
    if delimiter not in old_node.text:
        return [old_node]

    sp = old_node.text.split(delimiter, 1)

    if len(sp) <= 1:
        return [old_node]

    left = TextNode(sp[0], TextType.TEXT)
    rest = sp[1]

    if delimiter not in rest:
        raise Exception(f"unmatched delimiter found in {old_node.text}")

    rest_sp = rest.split(delimiter, 1)

    mid = TextNode(rest_sp[0], text_type)
    right = TextNode(rest_sp[1], TextType.TEXT)

    return [left, mid] + split_node_delimiter(right, delimiter, text_type)


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
