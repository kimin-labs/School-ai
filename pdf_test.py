from backend.tie_loader import TIEBookLoader
import os

path = r"C:\Users\brkra\OneDrive\Desktop\TIE\tie_books\chemistry_form1.pdf"
print('exists', os.path.exists(path))
loader = TIEBookLoader(r"C:\Users\brkra\OneDrive\Desktop\TIE\tie_books")
print('initial books', loader.list_books())

# directly call _extract_text_from_pdf to see chunks and pages
chunks,pages = loader._extract_text_from_pdf(path)
print('extracted chunks', len(chunks))
for idx in range(min(5,len(chunks))):
    print(f"chunk {idx} (page {pages[idx]}): {chunks[idx][:200]}")
