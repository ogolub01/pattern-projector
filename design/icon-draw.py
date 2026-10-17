from PIL import Image, ImageDraw, ImageFont
import math
BG=(14,14,13); BRASS=(201,162,75); INK=(237,234,226); GRID=(62,57,46)
def bez(p0,p1,p2,p3,n=60):
    return [(((1-t)**3)*p0[0]+3*((1-t)**2)*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0],
             ((1-t)**3)*p0[1]+3*((1-t)**2)*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]) for t in [i/n for i in range(n+1)]]
def sleeve():
    # symmetric about x = 0.5, and shifted so its height is centred on y = 0.5
    dy=-0.0225
    L=(0.27,0.44+dy); T=(0.50,0.255+dy); R=(0.73,0.44+dy)
    cap=bez(L,(0.34,0.43+dy),(0.375,0.255+dy),T)+bez(T,(0.625,0.255+dy),(0.66,0.43+dy),R)[1:]
    return cap+[(0.655,0.79+dy),(0.345,0.79+dy),L], cap
def bodice():
    pts=[(0.30,0.37)]
    pts+=bez((0.30,0.37),(0.38,0.37),(0.43,0.31),(0.445,0.24))[1:]          # neckline
    pts+=[(0.655,0.295)]                                                    # shoulder
    pts+=bez((0.655,0.295),(0.64,0.40),(0.66,0.47),(0.715,0.49))[1:]        # armhole
    pts+=[(0.69,0.775)]                                                     # side seam
    pts+=bez((0.69,0.775),(0.55,0.785),(0.40,0.79),(0.30,0.785))[1:]        # waist
    pts+=[(0.30,0.37)]
    return pts
def draw(piece, frame='full', notches=False, grain=False, cross=True, N=1024):
    S=N*2; im=Image.new('RGB',(S,S),BG); d=ImageDraw.Draw(im); f=S
    P=lambda q:(q[0]*f,q[1]*f)
    m=0.155; w=int(0.0145*S)
    # grid inside the frame
    g0,g1=m+0.06,1-m-0.06
    for i in range(1,5):
        t=g0+(g1-g0)*i/5
        d.line([P((t,g0)),P((t,g1))],fill=GRID,width=max(2,int(0.004*S)))
        d.line([P((g0,t)),P((g1,t))],fill=GRID,width=max(2,int(0.004*S)))
    # brass frame
    if frame=='full':
        d.rectangle([P((m,m)),P((1-m,1-m))],outline=BRASS,width=w)
    else:
        L=0.13
        for (x,y,dx,dy) in [(m,m,1,1),(1-m,m,-1,1),(m,1-m,1,-1),(1-m,1-m,-1,-1)]:
            # one polyline per corner so the joint is closed (no notch at the corner)
            d.line([P((x+dx*L,y)),P((x,y)),P((x,y+dy*L))],fill=BRASS,width=w,joint='curve')
            r=w/2; d.rectangle([P((x,y))[0]-r,P((x,y))[1]-r,P((x,y))[0]+r,P((x,y))[1]+r],fill=BRASS)
    pw=int(0.0135*S)
    if piece=='sleeve':
        outline,cap=sleeve()
        d.line([P(q) for q in outline],fill=INK,width=pw,joint='curve')
        if notches:
            def tick(i,k=1,off=0.0):
                a=cap[i]; b=cap[i+1]; tx,ty=b[0]-a[0],b[1]-a[1]; l=math.hypot(tx,ty); nx,ny=ty/l,-tx/l
                for j in range(k):
                    s=(j-(k-1)/2)*0.018; ax=a[0]+tx/l*s; ay=a[1]+ty/l*s
                    d.line([P((ax-nx*0.03,ay-ny*0.03)),P((ax+nx*0.02,ay+ny*0.02))],fill=BRASS,width=int(pw*0.9))
            tick(len(cap)//2)            # shoulder notch at the top of the cap
            tick(len(cap)//4,1)          # front: single notch
            tick(3*len(cap)//4,2)        # back: double notch
    else:
        pts=bodice(); d.line([P(q) for q in pts],fill=INK,width=pw,joint='curve')
        # waist dart
        d.line([P((0.455,0.785)),P((0.49,0.55)),P((0.525,0.783))],fill=INK,width=int(pw*0.8),joint='curve')
        # centre front fold: dashed brass
        if notches:
            y=0.40
            while y<0.76: d.line([P((0.30,y)),P((0.30,min(y+0.035,0.76)))],fill=BRASS,width=int(pw*1.2)); y+=0.06
    if grain:
        x=0.505 if piece=='sleeve' else 0.585; y0,y1=(0.40,0.70) if piece=='sleeve' else (0.42,0.70)
        d.line([P((x,y0)),P((x,y1))],fill=BRASS,width=int(pw*0.8))
        for yy,s in [(y0,1),(y1,-1)]: d.line([P((x-0.022,yy+s*0.03)),P((x,yy)),P((x+0.022,yy+s*0.03))],fill=BRASS,width=int(pw*0.8),joint='curve')
    if cross:
        cx,cy=(0.50,0.50) if piece=='sleeve' else (0.60,0.62); r=0.028
        if not grain:
            # the app's rotation-point mark: a small circle with four ticks (same proportions as #pivotMark, 26 px box)
            u=0.052/12; sw=int(pw*0.8)
            d.ellipse([P((cx-6*u,cy-6*u)),P((cx+6*u,cy+6*u))],outline=BRASS,width=sw)
            for (ax,ay,bx,by) in [(0,-12,0,-5),(0,5,0,12),(-12,0,-5,0),(5,0,12,0)]:
                d.line([P((cx+ax*u,cy+ay*u)),P((cx+bx*u,cy+by*u))],fill=BRASS,width=sw)
    return im.resize((N,N),Image.LANCZOS)
def rounded(im,n):
    s=im.resize((n,n),Image.LANCZOS); mask=Image.new('L',(n*4,n*4),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,n*4-1,n*4-1],radius=int(n*4*0.225),fill=255)
    out=Image.new('RGBA',(n,n),(0,0,0,0)); out.paste(s,(0,0),mask.resize((n,n),Image.LANCZOS)); return out
opts=[('A','Sleeve · frame',dict(piece='sleeve',frame='full')),
      ('B','Sleeve · notches + grain',dict(piece='sleeve',frame='full',notches=True,grain=True,cross=False)),
      ('C','Bodice · frame',dict(piece='bodice',frame='full')),
      ('D','Bodice · corners + fold',dict(piece='bodice',frame='corners',notches=True,grain=True,cross=False))]
W=4*300+5*40; H=300+120+160
sheet=Image.new('RGB',(W,H),(242,240,234)); sd=ImageDraw.Draw(sheet)
try:
    fb=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf',30); fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',15)
except: fb=fs=ImageFont.load_default()
for k,(key,label,kw) in enumerate(opts):
    im=draw(**kw); im.save(f'icon-{key}.png')
    x=40+k*340
    sheet.paste(rounded(im,300),(x,40),rounded(im,300))
    sd.text((x,360),key,fill=(30,30,28),font=fb); sd.text((x+34,372),label.upper(),fill=(110,106,98),font=fs)
    sm=rounded(im,64); sheet.paste(sm,(x,420),sm); sm2=rounded(im,40); sheet.paste(sm2,(x+84,432),sm2)
    sd.text((x+136,440),'home-screen sizes',fill=(140,136,128),font=fs)
sheet.save('icon-options.png')
