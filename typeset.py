import math

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from translate import TranslatedBlurb


def flow_into_box(text, w, font=None, min_word_on_line=0.3):
    def text_width(l):
        if l:
            return d.textsize(l, font=font)[0]
        else:
            return 0

    # fix text type...
    text = text.decode(encoding="utf-8")
    dImg = Image.new("RGB", (100, 100))
    d = ImageDraw.Draw(dImg)
    lines = []
    idx = 0
    line = ""
    while idx < len(text):
        if not line and text[idx] == " ":
            idx += 1
        running_width = text_width(line)
        next_token = text.find(" ", idx + 1)
        if next_token != -1:
            c_text = text[idx:next_token]
        else:
            c_text = text[idx:]
        c_width = text_width(c_text)
        proportion_of_fit = float(w - running_width) / c_width
        if proportion_of_fit > 0.95:
            line += c_text
            idx += len(c_text)
        #        elif proportion_of_fit > min_word_on_line:
        #            split = max(int(proportion_of_fit * len(c_text)), 1)
        #            c_text = c_text[:split] + "-"
        #            line += c_text
        #            idx += len(c_text) - 1
        else:
            if len(line) > 0:
                lines.append(line)
                line = ""
            else:
                split = max(int(proportion_of_fit * len(c_text)) // 2, 1)
                c_text = c_text[:split] + "-"
                lines.append(c_text)
                idx += len(c_text) - 1

    def safe_ascii(txt):
        if type(txt) is str:
            txt = txt.encode("ascii", "ignore")
        if type(txt) is bytes:
            txt = txt.decode("utf-8").encode("ascii", "ignore")
        return txt.decode("ascii", "ignore")

    if len(line) > 0:
        lines.append(safe_ascii(line))

    # ensure that it it can be latin encoded
    # print(lines)
    return "\n".join(lines)


def typeset_blurb(img, blurb):
    if isinstance(blurb, TranslatedBlurb):
        text = blurb.translation
    else:
        text = blurb.text

    area = blurb.w * blurb.h
    fontsize = int(math.sqrt(area) / 10)
    # usingFont = ImageFont.truetype(font="ccwildword.ttf", size=fontsize)
    # usingFont = ImageFont.truetype(font="arial.ttf", size=fontsize)
    usingFont = ImageFont.truetype(font="framd.ttf", size=fontsize)

    # pickle.dump(img, open("tts.pkl", mode="w"))
    flowed = flow_into_box(text, blurb.w, usingFont)
    flowed = flowed.encode("latin-1", "replace").decode("latin-1", "ignore")
    flowed = flowed.strip()
    d = ImageDraw.Draw(img)
    print("\tflowed:\n", flowed)
    size = d.textsize(flowed)
    x = (blurb.x + blurb.w / 2) - (size[0] / 2)
    y = (blurb.y + blurb.h / 2) - (size[1] / 2)
    x = int(x)
    y = int(y)
    img.paste((255, 255, 255), (x, y, x + size[0], y + size[1]))
    d.text((x, y), flowed.strip(), fill=(87, 6, 6))
