import re
from block import BlockType
from htmlnode import LeafNode, ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


def _split_node_delimiter(
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
    ] + _split_node_delimiter(right, delimiter, text_type)


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    res = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            res += _split_node_delimiter(node, delimiter, text_type)
        else:
            res += [node]

    return res


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[(.*?)\]\((.*?)\)", text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?<!!)\[(.*?)\]\((.*?)\)", text)


def _split_node_image_link(node: TextNode, image: bool) -> list[TextNode]:
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
            res += _split_node_image_link(node, True)
        else:
            res += [node]

    return res


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    res = []
    for node in old_nodes:
        if node.text_type == TextType.TEXT:
            res += _split_node_image_link(node, False)
        else:
            res += [node]

    return res


def text_to_text_nodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT, None)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes


def markdown_to_blocks(markdown: str) -> list[str]:
    return [
        x for x in map(lambda x: x.strip(), re.split(r"\n\s*?\n", markdown)) if x != ""
    ]


def block_to_block_type(block: str) -> BlockType:
    re_heading = re.compile(r"^#{1,6} .*$", re.DOTALL)
    re_code = re.compile(r"^```.*```$", re.DOTALL)
    re_quote = re.compile(r"^(?:>.*?\n)*(?:>.*?)$")
    re_unordered_list = re.compile(r"^(?:- .*?\n)*(?:- .*?)$")
    re_ordered_list = re.compile(r"^(?:\d\. .*?\n)*(?:\d\. .*?)$")

    if re_heading.match(block):
        return BlockType.HEADING
    elif re_code.match(block):
        return BlockType.CODE
    elif re_quote.match(block):
        return BlockType.QUOTE
    elif re_unordered_list.match(block):
        return BlockType.UNORDERED_LIST
    elif re_ordered_list.match(block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH


def conv_heading_to_div(md: str) -> ParentNode:
    marker, text_content = md.split(" ", 1)

    html_leafs = list(map(text_node_to_html_node, text_to_text_nodes(text_content)))

    return ParentNode(tag=f"h{len(marker)}", children=html_leafs)


def conv_code_to_div(md: str) -> LeafNode:
    return LeafNode(tag="code", value=md[3:-3])


def conv_quote_to_div(md: str) -> ParentNode:
    quote_lines = md.split("\n")
    text_content = "".join(map(lambda x: x[1:], quote_lines))
    html_leafs = list(map(text_node_to_html_node, text_to_text_nodes(text_content)))

    return ParentNode(tag="blockquote", children=html_leafs)


def conv_list_to_div(md: str, ordered: bool) -> ParentNode:
    list_lines = md.split("\n")

    lines_html_nodes = []

    for line in list_lines:
        text_content = line[2:]
        line_text_nodes = list(
            map(text_node_to_html_node, text_to_text_nodes(text_content))
        )

        lines_html_nodes.append(ParentNode(tag="li", children=line_text_nodes))

    if ordered:
        tag = "ol"
    else:
        tag = "ul"

    return ParentNode(tag=tag, children=lines_html_nodes)


def conv_paragraph_to_div(md: str) -> ParentNode:
    paragraph_text_nodes = list(map(text_node_to_html_node, text_to_text_nodes(md)))

    return ParentNode(tag="p", children=paragraph_text_nodes)


def markdown_to_html_node(markdown: str) -> ParentNode:
    blocks = list(
        map(
            lambda block: (block, block_to_block_type(block)),
            markdown_to_blocks(markdown),
        )
    )

    children = []

    for block in blocks:
        match block[1]:
            case BlockType.HEADING:
                children.append(conv_heading_to_div(block[0]))
            case BlockType.CODE:
                children.append(conv_code_to_div(block[0]))
            case BlockType.QUOTE:
                children.append(conv_quote_to_div(block[0]))
            case BlockType.UNORDERED_LIST:
                children.append(conv_list_to_div(block[0], ordered=False))
            case BlockType.ORDERED_LIST:
                children.append(conv_list_to_div(block[0], ordered=True))
            case BlockType.PARAGRAPH:
                children.append(conv_paragraph_to_div(block[0]))
            case _:
                raise NotImplementedError("OOOOOOOOOOOOO")

    return ParentNode("div", children=children)
