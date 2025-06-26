# Sample Document for Pandoc Converter Testing

This is a comprehensive test document designed to verify the functionality of our Pandoc converter application. It contains various elements that should be properly converted to different output formats.

## Text Formatting Examples

This paragraph contains **bold text**, *italic text*, and `inline code`. It also includes a [link to Pandoc's official website](https://pandoc.org).

## Lists

### Unordered List

- First item with regular text
- Second item with **bold formatting**
- Third item with *italic formatting*
- Fourth item with nested content:
  - Nested item 1
  - Nested item 2

### Ordered List

1.  Step one: Upload your document
2.  Step two: Select output format
3.  Step three: Click convert
4.  Step four: Download the result

## Images

<div class="image-container">

![Sample landscape image](output\26ed3d35-8f2c-40f8-92e7-6d4dba617cb3\media/34d9ea8795f10b4be125c77e110108f86b197cbe.jpg)

*Figure 1: A beautiful landscape (this image should be extracted during conversion)*

</div>

<div class="image-container">

![Technology image](output\26ed3d35-8f2c-40f8-92e7-6d4dba617cb3\media/e68b9be37bb0dba61153304c636e17a5dad9c099.jpg)

*Figure 2: Technology and coding (another test image)*

</div>

## Code Block

<div class="code-block">

function convertDocument(inputFile, outputFormat) { const pandocCommand = \`pandoc \${inputFile} -f html -t \${outputFormat} --extract-media=./media\`; return executeCommand(pandocCommand); }

</div>

## Table

| Input Format   | Extension | Pandoc Support | Notes                              |
|----------------|-----------|----------------|------------------------------------|
| Microsoft Word | .docx     | Excellent      | Full support with media extraction |
| HTML           | .html     | Excellent      | Native web format                  |
| Markdown       | .md       | Excellent      | Pandoc's native format             |
| LaTeX          | .tex      | Excellent      | Academic document format           |

## Blockquote

<div class="highlight">

**Important Note:** This document serves as a comprehensive test case for the Pandoc converter. When converted to Markdown, all formatting should be preserved, images should be extracted to a media folder, and relative paths should be correctly inserted.

</div>

> "Pandoc is a universal document converter. If you need to convert files from one markup format into another, pandoc is your swiss-army knife." - John MacFarlane, Creator of Pandoc

## Mathematical Expression

Here's a simple mathematical expression: E = mc²

And here's a more complex one that should be handled properly:

∫₀^∞ e^(-x²) dx = √π/2

## Special Characters and Unicode

This section tests various special characters:

- Arrows: → ← ↑ ↓ ⟷
- Mathematical: ∑ ∏ ∫ ∂ ∇ ∞
- Currency: \$ € £ ¥ ₹
- Symbols: © ® ™ § ¶ †
- Accented characters: café, naïve, résumé

## Conclusion

This test document contains a variety of elements commonly found in documents:

- Multiple heading levels
- Various text formatting options
- Images that should be extracted
- Tables with proper structure
- Lists (both ordered and unordered)
- Code blocks and inline code
- Special characters and Unicode
- Links and references

When this document is processed through the Pandoc converter, all these elements should be properly converted to the target format while maintaining their structure and meaning.

------------------------------------------------------------------------

<span class="small">Generated for testing the Pandoc Converter Application - Test completed successfully if you can read this in the converted format!</span>
