from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER, INK, WHITE = '#F7F3EA', '#17191C', '#FFFFFF'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
im = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(im)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, f, width):
    lines, current = [], ''
    for word in text.split():
        trial = word if not current else current + ' ' + word
        if d.textbbox((0, 0), trial, font=f)[2] <= width:
            current = trial
        else:
            if not current:
                raise ValueError(f'Word wider than available space: {word}')
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def line_height(text, f):
    box = d.textbbox((0, 0), text, font=f)
    return box[3] - box[1]


def fit(text, path, start, minimum, width, height, leading):
    for size in range(start, minimum - 1, -1):
        f = font(path, size)
        lines = wrap(text, f, width)
        total = sum(line_height(line, f) for line in lines) + max(0, len(lines) - 1) * leading
        if total <= height:
            return f, lines
    raise AssertionError(f'Text does not fit its panel: {text}')


def draw_text(text, path, start, minimum, box, fill, leading):
    x, y, width, height = box
    f, lines = fit(text, path, start, minimum, width, height, leading)
    assert all(d.textbbox((0, 0), line, font=f)[2] <= width for line in lines)
    assert sum(line_height(line, f) for line in lines) + max(0, len(lines) - 1) * leading <= height
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += line_height(line, f) + leading
    return f.size, len(lines)


def header(x, y, w, h, color, label, size):
    d.rectangle((x, y, x + w, y + h), fill=color)
    d.text((x + 14, y + 6), label, font=font(BOLD, size), fill=WHITE)


def globe_dove(cx, cy):
    d.ellipse((cx - 67, cy - 67, cx + 67, cy + 67), outline=WHITE, width=5)
    d.arc((cx - 40, cy - 67, cx + 40, cy + 67), 0, 360, fill=WHITE, width=3)
    d.arc((cx - 67, cy - 31, cx + 67, cy + 31), 0, 360, fill=WHITE, width=3)
    d.polygon([(cx-55,cy-22),(cx-10,cy-25),(cx+5,cy-43),(cx+17,cy-25),(cx+51,cy-27),(cx+29,cy-12),(cx+58,cy-4),(cx+18,cy+1),(cx+4,cy+27),(cx-8,cy+2),(cx-46,cy+8),(cx-23,cy-6)], fill=WHITE)
    d.polygon([(cx+49,cy-27),(cx+70,cy-34),(cx+57,cy-22)], fill=WHITE)


def ship(x, y):
    s = .72
    d.polygon([(x,y+48*s),(x+130*s,y+48*s),(x+111*s,y+72*s),(x+19*s,y+72*s)], fill=WHITE)
    d.rectangle((x+24*s,y+22*s,x+108*s,y+48*s), fill=WHITE)
    for i in range(3):
        d.rectangle((x+(33+25*i)*s,y+8*s,x+(53+25*i)*s,y+22*s), fill=WHITE)
    for j in range(2):
        d.arc((x+j*55*s,y+64*s,x+55*s+j*55*s,y+88*s),0,180,fill=WHITE,width=3)


def chip(x, y):
    d.rectangle((x+20,y+20,x+90,y+90), outline=WHITE, width=5)
    d.rectangle((x+38,y+38,x+72,y+72), outline=WHITE, width=3)
    for n in range(4):
        p=31+n*16
        d.line((x+p,y+7,x+p,y+20),fill=WHITE,width=4); d.line((x+p,y+90,x+p,y+103),fill=WHITE,width=4)
        d.line((x+7,y+p,x+20,y+p),fill=WHITE,width=4); d.line((x+90,y+p,x+103,y+p),fill=WHITE,width=4)
    d.line((x+95,y+16,x+75,y+34),fill=WHITE,width=7)
    d.polygon([(x+72,y+30),(x+75,y+44),(x+85,y+35)],fill=WHITE)


def outage(x, y):
    d.rectangle((x+9,y+25,x+103,y+83),outline=WHITE,width=5)
    d.line((x+10,y+27,x+56,y+63,x+103,y+27),fill=WHITE,width=4)
    d.line((x+61,y+35,x+48,y+51,x+61,y+58,x+52,y+75),fill='#1974B8',width=7)


def hospital(x, y):
    d.ellipse((x+14,y+10,x+98,y+94),outline=WHITE,width=5)
    d.rectangle((x+49,y+26,x+63,y+75),fill=WHITE); d.rectangle((x+32,y+44,x+80,y+58),fill=WHITE)
    d.polygon([(x+92,y+68),(x+118,y+68),(x+105,y+45)],fill=WHITE)
    d.line((x+105,y+52,x+105,y+60),fill='#45494E',width=3); d.ellipse((x+103,y+63,x+107,y+67),fill='#45494E')

# Masthead and lead.
d.rectangle((0,0,W,108),fill='#101316')
d.text((24,10),'THE WORLD IN ONE DAY',font=font(BOLD,48),fill=WHITE)
d.text((27,70),'FRIDAY, 13 NOVEMBER 2026',font=font(BOLD,20),fill='#E4E5E6')
header(0,108,W,48,'#123B63','LEAD',22)
lead_head='EUROPE JOINS UKRAINE PEACE TALKS'
lead_summary="Russia agrees to European seats at the next round after US envoys Kushner and Witkoff meet Putin in Moscow, then Zelenskyy near Dublin. Work begins on the war's largest prisoner exchange."
lead_h=draw_text(lead_head,BOLD,38,27,(24,169,735,53),INK,3)
lead_s=draw_text(lead_summary,REGULAR,23,17,(24,226,735,157),INK,5)
globe_dove(894,286)

# Four reports in a two-by-two grid.
stories=[
('HORMUZ ON EDGE','Four tankers hit in the Strait of Hormuz. Iran says a naval mine struck an LNG tanker and claims it destroyed a US radar in Bahrain.','#B7352A',ship),
('NVIDIA SHAKE-UP','Founder-CEO Jensen Huang resigns after 33 years. CFO Colette Kress takes over as interim chief. Shares fell up to 14% before closing 4.3% down.','#267044',chip),
('MICROSOFT DOWN',"Outlook and Teams fail around the world as Microsoft's mail and collaboration services go offline.",'#1974B8',outage),
('GAZA HOSPITAL STRIKE','An Israeli strike on Nasser hospital in Khan Younis kills six people, including a surgeon.','#45494E',hospital),
]
report=[(lead_head,*lead_h),(lead_summary,*lead_s)]
row_h=(870-405)//2
for i,(title,summary,color,icon) in enumerate(stories):
    x=(i%2)*512; y=405+(i//2)*row_h
    d.rectangle((x,y,x+512,y+row_h),fill=PAPER,outline='#A9A49A',width=2)
    header(x,y,512,43,color,title,21)
    icon(x+385,y+65)
    th=draw_text(title,BOLD,27,18,(x+16,y+54,340,48),INK,2)
    ts=draw_text(summary,REGULAR,18,14,(x+16,y+108,350,row_h-118),INK,3)
    report.extend([(title,*th),(summary,*ts)])

# Bottom "also today" strip.
d.rectangle((0,870,W,H),fill=PAPER)
header(0,870,W,40,'#25282B','ALSO TODAY',20)
also='Van Hollen challenges Schumer for Senate leadership • Justice Dept. moves to seize $1.2B in Binance-hack crypto • Google unveils Gemini 4 Hydrogen for Search • England beats Croatia into Nations League quarters • Storm Charles lashes Portugal • Pope Leo meets abuse survivors in Peru'
also_layout=draw_text(also,REGULAR,19,14,(19,921,986,94),INK,5)
report.append((also,*also_layout))
assert d.textbbox((24,10),'THE WORLD IN ONE DAY',font=font(BOLD,48))[2] <= W-20
im.save('entry.png',format='PNG',optimize=True)
print('Layout report (text | font size | line count)')
for label,size,count in report:
    print(f'{label} | {size}px | {count} line(s)')
print('Image: 1024x1024 PNG')
