import unittest

from parser import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
)
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


if __name__ == "__main__":
    unittest.main()
