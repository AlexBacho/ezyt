from image_utils import ImageText

def add_colored_text(text, output, image=None):
    main_color = (255,255,255)
    second_color = (255,0,0)
    padding_x = 10
    padding_y = 10
    margin_x = 0
    margin_y = 0
    words_to_highlight = ["reddit", "day"]
    words = text.split(" ")
    xy = (margin_x, margin_y)
    size = (800, 600)
    img = ImageText(size)
    font = "resources/font_tumbnail_abeezee.otf"
    font_size = 31
    for word in words:
        if word.lower() in words_to_highlight:
            color = second_color
        else:
            color = main_color
        offset = img.write_text(xy, word, font, font_size=font_size, color=color)
        xy = (xy[0] + offset[0] + padding_x, xy[1])
        if xy[0] > size[0] / 2:
            xy = (margin_x, offset[1] + padding_y)
    img.save(output)

if __name__ == "__main__":
    text = "hello reddit, how has your day been going so far?"
    out = "tmp.png"
    add_colored_text(text, out)
            