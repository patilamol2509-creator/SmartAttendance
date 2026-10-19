import sys, qrcode
if len(sys.argv)<2:
    print('Usage: python generate_qr.py 101 ["Student Name"]'); raise SystemExit(1)
roll=sys.argv[1].strip()
filename=f"student_{roll}_qr.png"
qrcode.make(f"STUDENT:{roll}").save(filename)
print(f"Created {filename}; QR content is STUDENT:{roll}")\n