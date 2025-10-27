import re
from datetime import datetime, timedelta

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


def is_psalm_119(chapter: int, book: str) -> bool:
    return (chapter == 119) and ("psalm" in book.lower())

def is_in_todays_psalm_119_range(verse: int, day_offset: int) -> bool:
    MCHEYNE_119 = {
        "June 22": [i for i in range(1,25)],
        "June 23": [i for i in range(25,49)],
        "June 24": [i for i in range(49,73)],
        "June 25": [i for i in range(73,97)],
        "June 26": [i for i in range(97,121)],
        "June 27": [i for i in range(121,145)],
        "June 28": [i for i in range(145,177)],
        "October 25": [i for i in range(1,25)],
        "October 26": [i for i in range(25,49)],
        "October 27": [i for i in range(49,73)],
        "October 28": [i for i in range(73,97)],
        "October 29": [i for i in range(97,121)],
        "October 30": [i for i in range(121,145)],
        "October 31": [i for i in range(145,177)],
        }
    target_date = datetime.now() + timedelta(days=day_offset)
    day_num = target_date.day
    month_name = target_date.strftime("%B")
    month_day = f"{month_name} {day_num}"
    verse_range = MCHEYNE_119[month_day]
    return verse in verse_range

def render_psalm_119(text: str, verse: int, day_offset: int, text_only: bool) -> str:
    HEBREW_ALEPHS = [
        "א", "ב", "ג",
        "ד", "ה", "ו",
        "ז", "ח", "ט",
        "י", "כ", "ל",
        "מ", "נ", "ס",
        "ע", "פ", "צ",
        "ק", "ר", "ש", "ת"
        ]
    HEBREW_ENGS = [
        "Aleph", "Beth", "Gimel",
        "Daleth", "He", "Waw",
        "Zayin", "Heth", "Teth",
        "Yod", "Kaph", "Lamed",
        "Mem", "Nun", "Samek",
        "Ayin", "Pe", "Tsade",
        "Qoph", "Resh", "Shin", "Tau"
        ]
    
    if is_in_todays_psalm_119_range(verse, day_offset):
    
        preamble = ""
        audio_preamble = ""

        if verse % 8 == 1:
            hebrew_aleph = HEBREW_ALEPHS[int(verse/8.01)]
            hebrew_eng = HEBREW_ENGS[int(verse/8.01)]
            preamble = f"""
            <div class="chapter-separator">
                <span class="small-caps">{hebrew_aleph} {hebrew_eng}</span>
            </div>
            """
            audio_preamble = hebrew_eng + "{{pause 2}}"
        verse_html = f"""{preamble}
                <div class="bible-text">
                    <span class="verse-number">{verse}.</span>{text}
                </div>
                """
        
        if text_only:
            return audio_preamble + text
        else: 
            return verse_html
    else:
        if text_only:
            return ""
        else:
            return "<span></span>"


def clean_verse_text(
        text: str, 
        verse: int, 
        chapter: int, 
        book: str, 
        day_offset: int,
        text_only: bool = False
        ) -> str:
    text = remove_footnotes(text)
    text = correct_quotations(text)
    text = correct_quotations(text)

    if is_psalm_119(chapter, book):
        return render_psalm_119(text, verse, day_offset, text_only)

    verse_html = f"""
            <div class="bible-text">
                <span class="verse-number">{verse}.</span>{text}
            </div>
            """
    if text_only:
        return text
    else:
        return verse_html

if __name__ == "__main__":
    for i in range (19):
        j = i + 1
        print(j, int(j/8.01))
    print("א")