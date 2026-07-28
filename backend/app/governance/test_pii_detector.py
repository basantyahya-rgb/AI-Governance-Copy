from app.governance.pii_detector import detect_pii

text = """
Email me at john@gmail.com
Phone 555-222-1234
"""

print(detect_pii(text))