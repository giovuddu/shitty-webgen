import unittest

from parser import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_text_nodes,
    markdown_to_blocks,
    block_to_block_type,
)
from block import BlockType


from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_basic_split(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold_split(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_italic_split(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_no_delimiter(self):
        node = TextNode("Just plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [node])

    def test_non_text_node_passthrough(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [node])

    def test_multiple_nodes(self):
        nodes = [
            TextNode("First **bold** text", TextType.TEXT),
            TextNode("already bold", TextType.BOLD),
            TextNode("Second _italic_ text", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("First ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
                TextNode("already bold", TextType.BOLD),
                TextNode("Second _italic_ text", TextType.TEXT),
            ],
        )

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This has **no closing", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_empty_delimiter_content(self):
        node = TextNode("This has **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This has ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_text_at_start(self):
        node = TextNode("**bold** at start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" at start", TextType.TEXT),
            ],
        )

    def test_text_at_end(self):
        node = TextNode("bold at **end**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("bold at ", TextType.TEXT),
                TextNode("end", TextType.BOLD),
            ],
        )


class TestExtractMarkdownImages(unittest.TestCase):
    def test_single_image(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_multiple_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            matches,
        )

    def test_no_images(self):
        text = "This is text with no images"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_empty_alt_text(self):
        text = "This is text with an ![](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_empty_url(self):
        text = "This is text with an ![image]()"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "")], matches)

    def test_special_characters_in_alt(self):
        text = "This is text with an ![image with spaces and symbols!](https://example.com/img.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("image with spaces and symbols!", "https://example.com/img.png")], matches
        )

    def test_special_characters_in_url(self):
        text = "This is text with an ![image](https://example.com/path-with-dashes_and_underscores.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("image", "https://example.com/path-with-dashes_and_underscores.png")],
            matches,
        )

    def test_image_at_start(self):
        text = "![first image](https://example.com/1.png) and some text"
        matches = extract_markdown_images(text)
        self.assertListEqual([("first image", "https://example.com/1.png")], matches)

    def test_image_at_end(self):
        text = "Some text and ![last image](https://example.com/2.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("last image", "https://example.com/2.png")], matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_single_link(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://www.boot.dev)"
        )
        self.assertListEqual([("link", "https://www.boot.dev")], matches)

    def test_multiple_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            matches,
        )

    def test_no_links(self):
        text = "This is text with no links"
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)

    def test_empty_anchor_text(self):
        text = "This is text with a [](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("", "https://www.boot.dev")], matches)

    def test_empty_url(self):
        text = "This is text with a [link]()"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "")], matches)

    def test_special_characters_in_anchor(self):
        text = (
            "This is text with a [link with spaces and symbols!](https://example.com)"
        )
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("link with spaces and symbols!", "https://example.com")], matches
        )

    def test_special_characters_in_url(self):
        text = "This is text with a [link](https://example.com/path-with-dashes_and_underscores.html)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("link", "https://example.com/path-with-dashes_and_underscores.html")],
            matches,
        )

    def test_link_at_start(self):
        text = "[first link](https://example.com/1) and some text"
        matches = extract_markdown_links(text)
        self.assertListEqual([("first link", "https://example.com/1")], matches)

    def test_link_at_end(self):
        text = "Some text and [last link](https://example.com/2)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("last link", "https://example.com/2")], matches)

    def test_mixed_images_and_links(self):
        text = "This has ![image](https://example.com/img.png) and [link](https://example.com/link.html)"
        image_matches = extract_markdown_images(text)
        link_matches = extract_markdown_links(text)
        self.assertListEqual([("image", "https://example.com/img.png")], image_matches)
        self.assertListEqual([("link", "https://example.com/link.html")], link_matches)


class TestSplitNodesImage(unittest.TestCase):
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

    def test_single_image(self):
        node = TextNode(
            "This is text with an ![image](https://example.com/img.png)", TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            ],
            new_nodes,
        )

    def test_no_images(self):
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_image_at_start(self):
        node = TextNode(
            "![first image](https://example.com/1.png) and some text", TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("first image", TextType.IMAGE, "https://example.com/1.png"),
                TextNode(" and some text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_image_at_end(self):
        node = TextNode(
            "Some text and ![last image](https://example.com/2.png)", TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Some text and ", TextType.TEXT),
                TextNode("last image", TextType.IMAGE, "https://example.com/2.png"),
            ],
            new_nodes,
        )

    def test_empty_alt_text(self):
        node = TextNode(
            "This is text with an ![](https://example.com/img.png)", TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("", TextType.IMAGE, "https://example.com/img.png"),
            ],
            new_nodes,
        )

    def test_empty_url(self):
        node = TextNode("This is text with an ![image]()", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, ""),
            ],
            new_nodes,
        )

    def test_non_text_node_passthrough(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([node], new_nodes)

    def test_multiple_nodes(self):
        nodes = [
            TextNode("First ![image1](https://example.com/1.png) text", TextType.TEXT),
            TextNode("already bold", TextType.BOLD),
            TextNode("Second ![image2](https://example.com/2.png) text", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        self.assertListEqual(
            [
                TextNode("First ", TextType.TEXT),
                TextNode("image1", TextType.IMAGE, "https://example.com/1.png"),
                TextNode(" text", TextType.TEXT),
                TextNode("already bold", TextType.BOLD),
                TextNode("Second ", TextType.TEXT),
                TextNode("image2", TextType.IMAGE, "https://example.com/2.png"),
                TextNode(" text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_special_characters_in_alt(self):
        node = TextNode(
            "This is text with an ![image with spaces and symbols!](https://example.com/img.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode(
                    "image with spaces and symbols!",
                    TextType.IMAGE,
                    "https://example.com/img.png",
                ),
            ],
            new_nodes,
        )

    def test_special_characters_in_url(self):
        node = TextNode(
            "This is text with an ![image](https://example.com/path-with-dashes_and_underscores.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode(
                    "image",
                    TextType.IMAGE,
                    "https://example.com/path-with-dashes_and_underscores.png",
                ),
            ],
            new_nodes,
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_single_link(self):
        node = TextNode(
            "This is text with a [link](https://example.com)", TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_no_links(self):
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_link_at_start(self):
        node = TextNode(
            "[first link](https://example.com/1) and some text", TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("first link", TextType.LINK, "https://example.com/1"),
                TextNode(" and some text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_link_at_end(self):
        node = TextNode(
            "Some text and [last link](https://example.com/2)", TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Some text and ", TextType.TEXT),
                TextNode("last link", TextType.LINK, "https://example.com/2"),
            ],
            new_nodes,
        )

    def test_empty_anchor_text(self):
        node = TextNode("This is text with a [](https://example.com)", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_empty_url(self):
        node = TextNode("This is text with a [link]()", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, ""),
            ],
            new_nodes,
        )

    def test_non_text_node_passthrough(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([node], new_nodes)

    def test_multiple_nodes(self):
        nodes = [
            TextNode("First [link1](https://example.com/1) text", TextType.TEXT),
            TextNode("already bold", TextType.BOLD),
            TextNode("Second [link2](https://example.com/2) text", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(nodes)
        self.assertListEqual(
            [
                TextNode("First ", TextType.TEXT),
                TextNode("link1", TextType.LINK, "https://example.com/1"),
                TextNode(" text", TextType.TEXT),
                TextNode("already bold", TextType.BOLD),
                TextNode("Second ", TextType.TEXT),
                TextNode("link2", TextType.LINK, "https://example.com/2"),
                TextNode(" text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_special_characters_in_anchor(self):
        node = TextNode(
            "This is text with a [link with spaces and symbols!](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode(
                    "link with spaces and symbols!",
                    TextType.LINK,
                    "https://example.com",
                ),
            ],
            new_nodes,
        )

    def test_special_characters_in_url(self):
        node = TextNode(
            "This is text with a [link](https://example.com/path-with-dashes_and_underscores.html)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode(
                    "link",
                    TextType.LINK,
                    "https://example.com/path-with-dashes_and_underscores.html",
                ),
            ],
            new_nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_text_nodes_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
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

    def test_plain_text(self):
        text = "Just plain text"
        nodes = text_to_text_nodes(text)
        self.assertListEqual([TextNode("Just plain text", TextType.TEXT)], nodes)

    def test_only_bold(self):
        text = "**bold text**"
        nodes = text_to_text_nodes(text)
        self.assertListEqual([TextNode("bold text", TextType.BOLD)], nodes)

    def test_only_italic(self):
        text = "_italic text_"
        nodes = text_to_text_nodes(text)
        self.assertListEqual([TextNode("italic text", TextType.ITALIC)], nodes)

    def test_only_code(self):
        text = "`code text`"
        nodes = text_to_text_nodes(text)
        self.assertListEqual([TextNode("code text", TextType.CODE)], nodes)

    def test_only_image(self):
        text = "![alt text](https://example.com/image.png)"
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [TextNode("alt text", TextType.IMAGE, "https://example.com/image.png")],
            nodes,
        )

    def test_only_link(self):
        text = "[link text](https://example.com)"
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [TextNode("link text", TextType.LINK, "https://example.com")], nodes
        )

    def test_multiple_bold(self):
        text = "This is **bold** and **more bold** text"
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("more bold", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
            nodes,
        )

    def test_multiple_italic(self):
        text = "This is _italic_ and _more italic_ text"
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("more italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
            nodes,
        )

    def test_multiple_code(self):
        text = "This is `code` and `more code` text"
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("more code", TextType.CODE),
                TextNode(" text", TextType.TEXT),
            ],
            nodes,
        )

    def test_multiple_images(self):
        text = "This is ![image1](https://example.com/1.png) and ![image2](https://example.com/2.png)"
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("image1", TextType.IMAGE, "https://example.com/1.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("image2", TextType.IMAGE, "https://example.com/2.png"),
            ],
            nodes,
        )

    def test_multiple_links(self):
        text = (
            "This is [link1](https://example.com/1) and [link2](https://example.com/2)"
        )
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("link1", TextType.LINK, "https://example.com/1"),
                TextNode(" and ", TextType.TEXT),
                TextNode("link2", TextType.LINK, "https://example.com/2"),
            ],
            nodes,
        )

    def test_empty_string(self):
        text = ""
        nodes = text_to_text_nodes(text)
        self.assertListEqual([], nodes)

    def test_text_with_special_characters(self):
        text = "Text with **bold** and _italic_ and `code` and ![image](https://example.com/img.png) and [link](https://example.com)"
        nodes = text_to_text_nodes(text)
        self.assertListEqual(
            [
                TextNode("Text with ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
            ],
            nodes,
        )


class TestMarkdownToBlocks(unittest.TestCase):
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

    def test_single_block(self):
        md = "Just one block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(["Just one block"], blocks)

    def test_multiple_paragraphs(self):
        md = "First paragraph\n\nSecond paragraph\n\nThird paragraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            ["First paragraph", "Second paragraph", "Third paragraph"], blocks
        )

    def test_leading_trailing_whitespace(self):
        md = """
        
        First block with spaces
        
        Second block with spaces
        
        """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            ["First block with spaces", "Second block with spaces"], blocks
        )

    def test_empty_blocks_removed(self):
        md = "First block\n\n\n\nSecond block\n\n\nThird block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(["First block", "Second block", "Third block"], blocks)

    def test_multiline_blocks(self):
        md = "First line\nSecond line\nThird line\n\nFourth line\nFifth line"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            ["First line\nSecond line\nThird line", "Fourth line\nFifth line"], blocks
        )

    def test_headings_and_paragraphs(self):
        md = "# Heading 1\n\nParagraph text\n\n## Heading 2\n\nMore text"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            ["# Heading 1", "Paragraph text", "## Heading 2", "More text"], blocks
        )

    def test_lists_and_code(self):
        md = "- List item 1\n- List item 2\n\n```\ncode block\n```\n\nParagraph"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            ["- List item 1\n- List item 2", "```\ncode block\n```", "Paragraph"],
            blocks,
        )

    def test_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual([], blocks)

    def test_only_newlines(self):
        md = "\n\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual([], blocks)


class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        block = "# Heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_multiple_levels(self):
        block = "###### Heading level 6"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_code(self):
        block = "```code block```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_multiline(self):
        block = "```\ncode line 1\ncode line 2\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_multiline(self):
        block = "> First line\n> Second line\n> Third line"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list(self):
        block = "- Item 1"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_multiple(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        block = "1. First item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_multiple(self):
        block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_paragraph(self):
        block = "This is a normal paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_multiline(self):
        block = "This is a paragraph\nwith multiple lines"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_no_space(self):
        block = "#No space after hash"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_not_closed(self):
        block = "```unclosed code block"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_quote_missing_prefix(self):
        block = "> First line\nSecond line without >"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_missing_space(self):
        block = "-No space after dash"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_missing_space(self):
        block = "1.No space after dot"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


if __name__ == "__main__":
    unittest.main()
