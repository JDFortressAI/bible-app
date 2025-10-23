import re

def remove_footnotes(text: str) -> str:
    """
    Removes footnotes in the format [a], [b], etc., along with a single space before them.
    """
    # Pattern to match a space followed by [single letter]
    pattern = r'\s\[[a-zA-Z]\]'
    # Replace with empty string
    return re.sub(pattern, '', text)

def correct_quotations(text: str) -> str:
    """
    Corrects spurious quotation marks.
    """
    pattern = r'[“”‘’][ ][“”‘’]'
    def convert_quotes(match):
        quote_map = {'“': '”', '‘': '’', '”': '”', '’': '’'}
        first_quote = quote_map[match.group(0)[0]]  # Convert first quote to closing
        second_quote = quote_map[match.group(0)[2]] # Convert second quote to closing
        return first_quote + second_quote
    return re.sub(pattern, convert_quotes, text)


def clean_verse_text(text, verse, chapter, book):
    text = remove_footnotes(text)
    text = correct_quotations(text)

    verse_html = f"""
            <div class="bible-text">
                <span class="verse-number">{verse}.</span>{text}
            </div>
            """
    return verse_html
