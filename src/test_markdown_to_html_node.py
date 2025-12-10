import unittest

from parser import markdown_to_html_node


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
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

    def test_headings(self):
        md = """
# Heading 1

### Smaller _heading_
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h3>Smaller <i>heading</i></h3></div>",
        )

    def test_unordered_list(self):
        md = """
- item one
- item _two_
- item with **bold**
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>item one</li><li>item <i>two</i></li><li>item with <b>bold</b></li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. first item
2. second `code`
3. third item
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>first item</li><li>second <code>code</code></li><li>third item</li></ol></div>",
        )

    def test_mixed_blocks(self):
        md = """
# Title

Paragraph with [link](https://example.com) inside it

>Quoted line with **bold**

- first bullet
- second bullet

```
raw_code()
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><h1>Title</h1><p>Paragraph with <a href="https://example.com">link</a> inside it</p><blockquote>Quoted line with <b>bold</b></blockquote><ul><li>first bullet</li><li>second bullet</li></ul><pre><code>raw_code()\n</code></pre></div>',
        )


if __name__ == "__main__":
    unittest.main()
