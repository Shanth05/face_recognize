# generate_website_qr.py
import qrcode # type: ignore

def generate_website_qr():
    url = "https://yourwebsite.com"  # Replace with your actual website URL after deployment
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("website_qr.png")
    print("QR code saved as 'website_qr.png'. Print or share this with attendees.")

if __name__ == "__main__":
    generate_website_qr()