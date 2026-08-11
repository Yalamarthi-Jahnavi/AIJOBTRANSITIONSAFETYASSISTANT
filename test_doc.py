import sys
import os
sys.path.append(os.path.dirname(__file__))

from ai_service import analyze_offer_letter

dummy_text = """
OFFER OF EMPLOYMENT
Company: XYZ Tech Solutions
Role: Senior Software Engineer
Salary: $120,000 per annum
Joining Date: 2026-09-01
Location: Remote
Notice Period: 1 month by employee, 1 month by employer. No leave during notice period.
Probation: 6 months probation.
Background check: Subject to successful background verification check.
"""

print("Testing Offer Letter Analyzer...")
result = analyze_offer_letter(dummy_text)
print(result)
