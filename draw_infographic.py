from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1024, 1024
PAPER = '#F7F3EA'
INK = '#15191D'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
im = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(im)
report = []


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def gradient(box, top, bottom):
    x0, y0, x1, y1 = box
    h = max(1, y1-y0)
    def rgb(c):
        c = c.lstrip('#')
        return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
    a, b = rgb(top), rgb(bottom)
    strip = Image.new('RGB', (1, h))
    sd = ImageDraw.Draw(strip)
    for y in range(h):
        t = y / max(1, h-1)
        sd.point((0, y), fill=tuple(round(a[k]*(1-t)+b[k]*t) for k in range(3)))
    im.paste(strip.resize((x1-x0, h)), (x0, y0))


def glow(cx, cy, rx, ry):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for scale, col in ((1.0, (211, 48, 13, 65)), (.69, (255, 113, 16, 105)), (.36, (255, 219, 77, 185))):
        ld.ellipse((cx-rx*scale, cy-ry*scale, cx+rx*scale, cy+ry*scale), fill=col)
    im.paste(layer, (0, 0), layer)


def text_width(txt, f):
    b = f.getbbox(txt)
    return b[2]-b[0]


def wrap(txt, f, width):
    out, line = [], ''
    for word in txt.split():
        test = word if not line else line + ' ' + word
        if text_width(test, f) <= width:
            line = test
        else:
            if not line:
                raise AssertionError('single word wider than text area: '+word)
            out.append(line)
            line = word
    if line:
        out.append(line)
    return out


def draw_text_block(txt, xy, width, max_height, size, bold, color, min_size=8, leading=2, tag=''):
    x, y = xy
    chosen = None
    for s in range(size, min_size-1, -1):
        f = font(s, bold)
        lines = wrap(txt, f, width)
        line_h = f.getbbox('Ag')[3] - f.getbbox('Ag')[1]
        height = len(lines)*line_h + max(0, len(lines)-1)*leading
        assert all(text_width(line, f) <= width for line in lines)
        if height <= max_height:
            chosen = (f, lines, line_h, height, s)
            break
    if chosen is None:
        raise AssertionError(f'text overflows {tag}: {txt}')
    f, lines, line_h, height, s = chosen
    for line in lines:
        d.text((x, y), line, font=f, fill=color)
        y += line_h + leading
    report.append((tag, s, len(lines)))
    return y


def poly(points, fill, outline=None, width=1):
    d.polygon(points, fill=fill)
    if outline:
        d.line(points+[points[0]], fill=outline, width=width)


def ellipse(box, fill, outline=None, width=1):
    d.ellipse(box, fill=fill, outline=outline, width=width)


def draw_lead_scene(box):
    x0,y0,x1,y1=box
    gradient(box, '#101B2E', '#E86A24')
    # storm clouds
    for cx,cy,rx,ry,c in [(75,35,110,36,'#263343'),(220,53,140,43,'#1D2938'),(398,28,135,35,'#263344'),(593,52,126,38,'#222D3C'),(790,31,150,42,'#1B2736'),(964,61,110,36,'#293544')]:
        ellipse((cx-rx, y0+cy-ry, cx+rx, y0+cy+ry), c)
    # horizon firelight and rough sea
    glow(440, y0+167, 270, 81)
    d.rectangle((x0,y0+180,x1,y1), fill='#17374B')
    for i in range(19):
        yy=y0+185+i*4
        col=('#E88541' if i<3 else '#226076' if i%2 else '#17485D')
        d.line((x0,yy,x1,yy+((i%3)-1)*2), fill=col, width=2)
    # distant missile trails, smoke puffs
    for pts in [[(280,y0+73),(395,y0+91),(532,y0+115)],[(540,y0+66),(650,y0+81),(776,y0+109)],[(118,y0+86),(220,y0+104),(318,y0+123)]]:
        d.line(pts, fill='#D7D1C3', width=2)
        for px,py in pts[1:]:
            ellipse((px-9,py-5,px+9,py+5),'#66717A')
    # burning tanker
    hull=[(154,y0+175),(492,y0+175),(460,y0+206),(198,y0+206)]
    poly(hull,'#101820')
    d.rectangle((240,y0+146,423,y0+177),fill='#222B30')
    d.rectangle((266,y0+128,296,y0+147),fill='#D3D2C9')
    d.rectangle((362,y0+136,390,y0+147),fill='#CACBC6')
    d.line((274,y0+128,274,y0+109),fill='#222',width=4)
    for cx,cy,sz in [(278,112,32),(324,107,38),(367,115,29),(401,125,24)]:
        glow(cx,cy,sz,sz*1.2)
        poly([(cx-sz*.45,cy+sz*.35),(cx-sz*.2,cy-sz*.65),(cx+sz*.05,cy-sz*.24),(cx+sz*.42,cy-sz*.8),(cx+sz*.32,cy+sz*.4)],'#FF9C23')
        poly([(cx-sz*.19,cy+sz*.32),(cx,cy-sz*.5),(cx+sz*.22,cy+sz*.3)],'#FFE26B')
    # warship right with radar dome
    poly([(661,y0+180),(911,y0+180),(879,y0+201),(698,y0+201)],'#111A23')
    d.rectangle((715,y0+148,845,y0+181),fill='#25323A')
    d.rectangle((754,y0+130,783,y0+149),fill='#CFD4D4')
    d.pieslice((762,y0+109,798,y0+145),180,360,fill='#F1F3EE')
    d.rectangle((762,y0+127,798,y0+145),fill='#F1F3EE')
    d.line((740,y0+148,740,y0+117),fill='#111',width=3)
    d.line((819,y0+149,819,y0+120),fill='#111',width=3)
    # jets
    for cx,cy in [(570,y0+77),(856,y0+93),(107,y0+119)]:
        poly([(cx-15,cy),(cx+11,cy-4),(cx+19,cy),(cx+5,cy+4),(cx-11,cy+3)],'#0C121A')
    d.rectangle((x0,y1-2,x1,y1),fill='#F2A148')


def scene_negotiation(box):
    x0,y0,x1,y1=box
    gradient(box,'#263348','#947353')
    for cx,col in [(x0+74,'#244998'),(x0+162,'#1C5DB8'),(x0+250,'#B7B8B8')]:
        d.rectangle((cx-20,y0+10,cx+20,y0+61),fill=col)
        if cx==x0+162: d.rectangle((cx-20,y0+36,cx+20,y0+61),fill='#F4D34E')
        if cx==x0+250:
            d.rectangle((cx-20,y0+27,cx+20,y0+44),fill='#3968A8'); d.rectangle((cx-20,y0+44,cx+20,y0+61),fill='#C4413A')
        for a in range(8):
            ang=a*math.pi/4
            ellipse((cx+math.cos(ang)*12-2,y0+32+math.sin(ang)*12-2,cx+math.cos(ang)*12+2,y0+32+math.sin(ang)*12+2),'#F6D74C')
    # seated silhouettes and table
    for px in (x0+31,x0+274):
        ellipse((px-9,y0+51,px+9,y0+69),'#161C23')
        d.polygon([(px-15,y0+69),(px+15,y0+69),(px+20,y0+103),(px-20,y0+103)],fill='#222A31')
    ellipse((x0+60,y0+75,x1-60,y0+112),'#202832')
    poly([(x0+118,y0+75),(x0+157,y0+63),(x0+193,y0+80),(x0+167,y0+93),(x0+132,y0+91)],'#E8C960')
    glow(x0+155,y0+80,43,18)


def scene_chip(box):
    x0,y0,x1,y1=box
    gradient(box,'#092D2B','#071C20')
    for xx in range(x0+7,x1,25): d.line((xx,y0,xx+20,y1),fill='#17624F',width=1)
    for yy in range(y0+7,y1,19): d.line((x0,yy,x1,yy),fill='#125242',width=1)
    # chip and pins
    cb=(x0+100,y0+17,x0+196,y0+80)
    d.rectangle(cb,fill='#141A20',outline='#83B78A',width=3)
    for xx in range(cb[0]+8,cb[2],12):
        d.line((xx,y0+8,xx,y0+17),fill='#C6A547',width=3); d.line((xx,y0+80,xx,y0+89),fill='#C6A547',width=3)
    for yy in range(y0+25,y0+76,12):
        d.line((cb[0]-9,yy,cb[0],yy),fill='#C6A547',width=3); d.line((cb[2],yy,cb[2]+9,yy),fill='#C6A547',width=3)
    d.text((x0+120,y0+35),'NVIDIA',font=font(13,True),fill='#B7E37E')
    # falling arrow
    poly([(x0+216,y0+11),(x0+236,y0+28),(x0+229,y0+35),(x0+250,y0+55),(x0+237,y0+68),(x0+217,y0+48),(x0+208,y0+57)],'#F04A3A')


def scene_outage(box):
    x0,y0,x1,y1=box
    gradient(box,'#142648','#087D9A')
    for bx in (x0+20,x0+155):
        d.rounded_rectangle((bx,y0+13,bx+112,y0+79),radius=7,fill='#DDE6E9',outline='#5B718A',width=3)
    # envelope icon
    d.rectangle((x0+46,y0+34,x0+104,y0+67),fill='#507DB7')
    d.line((x0+46,y0+34,x0+75,y0+54,x0+104,y0+34),fill='white',width=3)
    # chat bubble
    d.rounded_rectangle((x0+180,y0+29,x0+229,y0+61),radius=10,fill='#44B79C')
    poly([(x0+188,y0+58),(x0+185,y0+70),(x0+201,y0+59)],'#44B79C')
    # yellow jagged crack
    poly([(x0+130,y0+3),(x0+117,y0+37),(x0+132,y0+34),(x0+119,y0+69),(x0+151,y0+31),(x0+137,y0+34)],'#FFD638')
    # warning triangle
    poly([(x1-31,y0+13),(x1-8,y0+57),(x1-54,y0+57)],'#F4473D')
    d.text((x1-35,y0+27),'!',font=font(25,True),fill='white')


def scene_taiwan(box):
    x0,y0,x1,y1=box
    gradient(box,'#87919A','#354A5A')
    # sea waves
    for yy in range(y0+46,y1,10): d.line((x0,yy,x1,yy+2),fill='#74828A',width=2)
    # island and target
    poly([(x0+100,y0+55),(x0+116,y0+43),(x0+134,y0+51),(x0+144,y0+69),(x0+135,y0+87),(x0+119,y0+94),(x0+104,y0+78)],'#758D5D')
    for rad in (15,27): d.ellipse((x0+123-rad,y0+68-rad,x0+123+rad,y0+68+rad),outline='#D8453F',width=3)
    d.line((x0+123,y0+37,x0+123,y0+99),fill='#D8453F',width=2); d.line((x0+92,y0+68,x0+154,y0+68),fill='#D8453F',width=2)
    # warship
    poly([(x0+17,y0+79),(x0+109,y0+79),(x0+96,y0+91),(x0+31,y0+91)],'#18212A')
    d.rectangle((x0+47,y0+64,x0+81,y0+80),fill='#202B34'); d.rectangle((x0+58,y0+56,x0+71,y0+65),fill='#A9B2B1')
    for cx,cy in [(x0+54,y0+24),(x0+205,y0+35)]:
        poly([(cx-17,cy),(cx+10,cy-4),(cx+18,cy),(cx+6,cy+4),(cx-12,cy+3)],'#19212A')


def scene_climate(box):
    x0,y0,x1,y1=box
    gradient(box,'#A6D5E7','#EDF0E5')
    # distant ice ridges
    poly([(x0,y0+55),(x0+44,y0+29),(x0+75,y0+58),(x0+110,y0+20),(x0+151,y0+59),(x0+193,y0+30),(x1,y0+60),(x1,y1),(x0,y1)],'#D8EFF1')
    poly([(x0+15,y0+68),(x0+75,y0+58),(x0+97,y0+74),(x0+140,y0+63),(x0+178,y0+77),(x1,y0+68),(x1,y1-9),(x0,y1-9)],'#B7DDE2')
    # polar bear
    ellipse((x0+47,y0+55,x0+91,y0+77),'#FBFCF7')
    ellipse((x0+83,y0+51,x0+101,y0+68),'#FBFCF7')
    for lx in (x0+55,x0+81): d.rounded_rectangle((lx,y0+69,lx+8,y0+86),radius=3,fill='#F7FAF8')
    ellipse((x0+96,y0+57,x0+99,y0+60),'#26353B')
    # cracked earth bottom
    poly([(x0,y1-20),(x0+35,y1-34),(x0+68,y1-24),(x0+98,y1-39),(x0+145,y1-28),(x0+197,y1-38),(x1,y1-20),(x1,y1),(x0,y1)],'#8C654A')
    for pts in [[(x0+31,y1-27),(x0+39,y1-11),(x0+51,y1-3)],[(x0+110,y1-32),(x0+105,y1-17),(x0+122,y1-4)],[(x0+177,y1-29),(x0+165,y1-15),(x0+175,y1-4)]]: d.line(pts,fill='#382D26',width=2)
    # leaf
    ellipse((x1-35,y0+13,x1-13,y0+27),'#5E9A51'); d.line((x1-33,y0+25,x1-13,y0+14),fill='#D8E6B2',width=2)


def scene_gaza(box):
    x0,y0,x1,y1=box
    gradient(box,'#454C54','#171C21')
    # smoke glow
    glow(x0+139,y0+48,67,43)
    # broken skyline
    for bx,bw,bh in [(x0,44,47),(x0+39,51,65),(x0+85,33,40),(x0+119,45,58),(x0+160,42,44),(x0+200,51,67),(x0+247,35,48)]:
        d.rectangle((bx,y0+76-bh,bx+bw,y0+77),fill='#272D32')
        for wx in range(bx+7,bx+bw-4,13):
            for wy in range(y0+22,y0+70,14):
                if (wx+wy)%3: d.rectangle((wx,wy,wx+4,wy+4),fill='#737064')
    # rubble foreground
    for pts in [[(x0,y1),(x0+36,y0+80),(x0+69,y1)],[(x0+88,y1),(x0+121,y0+84),(x0+151,y1)],[(x0+176,y1),(x0+207,y0+81),(x1,y1)]]: poly(pts,'#62615A')
    # hospital cross badge
    ellipse((x0+17,y0+8,x0+57,y0+48),'#E8E8DF')
    d.rectangle((x0+32,y0+15,x0+42,y0+41),fill='#D63F3D'); d.rectangle((x0+24,y0+23,x0+50,y0+33),fill='#D63F3D')
    # warning triangle
    poly([(x1-39,y0+11),(x1-14,y0+55),(x1-64,y0+55)],'#E5A33C')
    d.text((x1-44,y0+25),'!',font=font(25,True),fill='#302A20')

# Masthead
# black band, centered masthead, red rule and dateline
d.rectangle((0,0,W,88),fill='#11161B')
title='THE WORLD IN ONE DAY'
tf=font(37,True)
d.text(((W-text_width(title,tf))/2,7),title,font=tf,fill='white')
d.rectangle((24,53,W-24,57),fill='#D43B32')
dateline='FRIDAY, 13 NOVEMBER 2026'
df=font(15,True)
d.text(((W-text_width(dateline,df))/2,64),dateline,font=df,fill='#F4F0E8')

# Lead photograph and caption strip
lead_scene=(0,88,W,326)
draw_lead_scene(lead_scene)
d.rectangle((0,326,W,421),fill='#741F1B')
draw_text_block('IRAN CLAIMS STRIKE ON US RADAR; 4 TANKERS HIT IN HORMUZ',(24,333),976,31,21,True,'#FFFFFF',16,1,'LEAD HEADLINE')
draw_text_block('Iran says a naval mine struck an LNG tanker and claims it destroyed a US radar in Bahrain.',(24,371),976,40,15,False,'#FFF4E8',12,2,'LEAD SUMMARY')

stories=[
 ('EUROPE JOINS UKRAINE PEACE TALKS','Russia agrees to European seats at the next round after US envoys Kushner and Witkoff meet Putin in Moscow, then Zelenskyy near Dublin.',scene_negotiation),
 ('HUANG QUITS NVIDIA AFTER 33 YEARS','Founder-CEO Jensen Huang resigns amid scandal. CFO Colette Kress takes over as interim chief. Shares fell up to 14%.',scene_chip),
 ('MICROSOFT 365 GOES DARK WORLDWIDE',"Outlook and Teams fail around the world as Microsoft's mail and collaboration services go offline.",scene_outage),
 ('CHINA DRILLS AROUND TAIWAN','China holds unannounced Pacific drills around Taiwan as jets and warships circle the island.',scene_taiwan),
 ('COP31: CLIMATE ON THE EDGE','Leaders meet at COP31 as melting ice and record heat put climate action back at the top of the agenda.',scene_climate),
 ('GAZA HOSPITAL STRIKE KILLS SIX','An Israeli strike on Nasser hospital in Khan Younis kills six people, including a surgeon.',scene_gaza),
]
cols=3; gap=8; cw=(W-gap*(cols-1))//cols; ch=184; grid_y=429
for idx,(head,summary,scene) in enumerate(stories):
    row,col=divmod(idx,cols)
    x=col*(cw+gap); y=grid_y+row*(ch+gap)
    d.rectangle((x,y,x+cw,y+ch),fill='#E9E4DA',outline='#1C2228',width=1)
    scene((x+1,y+1,x+cw-1,y+91))
    d.rectangle((x+1,y+91,x+cw-1,y+ch-1),fill='#F7F3EA')
    headline_end=draw_text_block(head,(x+9,y+96),cw-18,37,14,True,'#171B1F',10,1,f'GRID {chr(97+idx)} HEADLINE')
    draw_text_block(summary,(x+9,headline_end+2),cw-18,y+ch-headline_end-7,11,False,'#30343A',8,1,f'GRID {chr(97+idx)} SUMMARY')

# Also today footer, with exact supplied news string
fy=813
d.rectangle((0,fy,W,H),fill='#171C20')
d.rectangle((0,fy,W,850),fill='#A6332B')
label='ALSO TODAY'; lf=font(21,True)
d.text((24,fy+5),label,font=lf,fill='white')
also='Justice Dept. moves to seize $1.2B in Binance-hack crypto • Oil slides on surplus fears • Van Hollen challenges Schumer for Senate leadership • Google unveils Gemini 4 Hydrogen for Search • England beats Croatia into Nations League quarters • Storm Charles lashes Portugal • Pope Leo meets abuse survivors in Peru'
draw_text_block(also,(24,864),976,145,18,False,'#F4F0E8',14,8,'ALSO TODAY')
# Small folio rule lends a print-front-page finish
d.rectangle((24,1007,W-24,1010),fill='#B74438')

im.save('entry.png',format='PNG',optimize=True)
print('LAYOUT REPORT')
for tag,size,count in report:
    print(f'{tag}: font={size}px lines={count}')
