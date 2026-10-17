import importlib.util, sys
spec=importlib.util.spec_from_file_location('d','draw.py'); src=open('draw.py').read().split("opts=[")[0]
ns={}; exec(src, ns)
from PIL import Image
big=ns['draw'](piece='sleeve', frame='corners', N=1024)
big.save('notch-1024.png')
out='/home/claude/pattern-projector/public/'
for n,name in [(512,'icon-512.png'),(192,'icon-192.png'),(180,'apple-touch-icon.png'),(32,'favicon.png')]:
    big.resize((n,n),Image.LANCZOS).save(out+name)
# maskable: same art shrunk into the safe zone so round masks don't clip the corners
m=Image.new('RGB',(512,512),(14,14,13)); m.paste(big.resize((420,420),Image.LANCZOS),(46,46)); m.save(out+'icon-maskable-512.png')
# preview next to home-screen sizes
ns2=ns; r=ns['rounded']
sheet=Image.new('RGB',(560,340),(242,240,234)); a=r(big,300); sheet.paste(a,(20,20),a)
for n,x in [(120,350),(64,350),(40,430)]:
    s=r(big,n); sheet.paste(s,(x if n!=64 else 350, 20 if n==120 else 170),s)
sheet.save('notch-preview.png')
