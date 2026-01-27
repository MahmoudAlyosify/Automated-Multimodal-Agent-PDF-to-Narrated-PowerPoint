from pathlib import Path
import os

# Test path detection
pdf_name = "A Beginner's Guide to Building Intelligence Through Patterns - gulli.pdf"
p = Path(pdf_name)

print(f"Current dir: {os.getcwd()}")
print(f"Path exists: {p.exists()}")
print(f"Absolute: {p.resolve()}")
print(f"String path: {str(p)}")

# List all files
print("\nAll PDF files in directory:")
for f in Path(".").glob("*.pdf"):
    print(f"  {f}")
