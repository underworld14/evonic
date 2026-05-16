#!/usr/bin/env python3
"""Convert pinchtab-feasibility-study.md to PDF using fpdf2 and NotoSans."""

from fpdf import FPDF
import re
import os

FONT_PATH = "/tmp/NotoSans-Regular.ttf"
FONT_BOLD = "/tmp/NotoSans-Bold.ttf"

# Download bold if needed
if not os.path.exists(FONT_BOLD):
    import urllib.request
    url = 'https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSans/NotoSans-Bold.ttf'
    try:
        urllib.request.urlretrieve(url, FONT_BOLD)
        print(f"Downloaded Bold: {os.path.getsize(FONT_BOLD)} bytes")
    except Exception as e:
        print(f"Bold font download failed: {e}")

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("NS", "", FONT_PATH, uni=True)
        if os.path.exists(FONT_BOLD):
            self.add_font("NS", "B", FONT_BOLD, uni=True)
        else:
            self.add_font("NS", "B", FONT_PATH, uni=True)
        self.add_page()
        self._in_code = False

    def header(self):
        if self.page_no() > 1:
            self.set_font("NS", "", 7)
            self.set_text_color(128, 128, 128)
            self.cell(0, 5, "PinchTab Feasibility Study for Evonic Platform", align="C")
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("NS", "", 7)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def para(self, text, size=9, style="", color=(0,0,0)):
        """Write a paragraph with auto-wrapping."""
        self.set_font("NS", style, size)
        self.set_text_color(*color)
        # Calculate available width
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, size * 0.65, text, align="L")
    
    def heading1(self, text):
        self.ln(3)
        self.set_font("NS", "B", 16)
        self.set_text_color(25, 60, 150)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 10, text)
        self.set_text_color(0, 0, 0)
        self.ln(2)
    
    def heading2(self, text):
        self.ln(3)
        self.set_font("NS", "B", 12)
        self.set_text_color(25, 60, 150)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 8, text)
        self.set_text_color(0, 0, 0)
        self.ln(1)
    
    def heading3(self, text):
        self.ln(2)
        self.set_font("NS", "B", 10)
        self.set_text_color(60, 60, 60)
        w = self.w - self.l_margin - self.r_margin
        self.multi_cell(w, 7, text)
        self.set_text_color(0, 0, 0)
        self.ln(1)
    
    def hr(self):
        self.ln(2)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
    
    def bullet(self, text, indent=10, size=9):
        self.set_font("NS", "", size)
        x0 = self.l_margin + indent
        self.set_x(x0)
        w = self.w - self.r_margin - x0
        self.multi_cell(w, size * 0.65, f"• {text}")

    def code_block(self, lines):
        """Render a code block using Unicode font for box-drawing support."""
        self.ln(2)
        self.set_fill_color(245, 245, 245)
        self.set_font("NS", "", 7)
        for line in lines:
            w = self.w - self.l_margin - self.r_margin - 4
            self.set_x(self.l_margin + 2)
            self.multi_cell(w, 4, line, fill=True)
        self.ln(2)
    
    def table(self, rows):
        if len(rows) < 2:
            return
        self.ln(2)
        ncols = len(rows[0])
        available = self.w - self.l_margin - self.r_margin
        col_w = available / ncols
        
        # Header
        self.set_font("NS", "B", 8)
        self.set_fill_color(25, 60, 150)
        self.set_text_color(255, 255, 255)
        for cell in rows[0]:
            self.cell(col_w, 6, cell, border=1, fill=True)
        self.ln()
        self.set_text_color(0, 0, 0)
        
        # Body
        self.set_font("NS", "", 8)
        for row in rows[1:]:
            for cell in row:
                self.cell(col_w, 5, cell, border=1)
            self.ln()
        self.ln(2)


def parse_and_render(pdf, content):
    lines = content.split("\n")
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i]
        
        # Code block
        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                pdf.code_block(code_lines)
            i += 1  # skip closing ```
            continue
        
        # Table
        if line.startswith("|") and "|" in line[1:]:
            table_rows = []
            # Capture header + separator + body
            while i < n and lines[i].startswith("|"):
                row_line = lines[i]
                # Skip separator rows like |---|---|
                if re.match(r"^\|[\s\-:|]+\|$", row_line):
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.split("|")[1:-1]]
                table_rows.append(cells)
                i += 1
            if table_rows:
                pdf.table(table_rows)
            continue
        
        # Headings
        if line.startswith("# ") and not line.startswith("## "):
            pdf.heading1(line[2:])
            i += 1
            continue
        if line.startswith("## "):
            pdf.heading2(line[3:])
            i += 1
            continue
        if line.startswith("### "):
            pdf.heading3(line[4:])
            i += 1
            continue
        
        # HR
        if line.strip() == "---":
            pdf.hr()
            i += 1
            continue
        
        # Bullet lists (collect consecutive bullets)
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            while i < n and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                pdf.bullet(lines[i].strip()[2:])
                i += 1
            continue
        
        # Numbered list
        if re.match(r"^\s*\d+\.\s", line):
            indent = len(line) - len(line.lstrip())
            while i < n and re.match(r"^\s*\d+\.\s", lines[i]):
                pdf.para(lines[i].strip(), size=9)
                i += 1
            continue
        
        # Blockquote
        if line.startswith("> "):
            pdf.set_text_color(100, 100, 100)
            pdf.set_font("NS", "I", 9)
            w = pdf.w - pdf.l_margin - pdf.r_margin - 10
            pdf.set_x(pdf.l_margin + 5)
            pdf.multi_cell(w, 5.5, line[2:])
            pdf.set_text_color(0, 0, 0)
            i += 1
            continue
        
        # Empty line
        if not line.strip():
            pdf.ln(2)
            i += 1
            continue
        
        # Normal paragraph
        pdf.para(line, size=9)
        i += 1


def main():
    md_path = "/workspace/pinchtab-feasibility-study.md"
    pdf_path = "/workspace/pinchtab-feasibility-study.pdf"
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    pdf = PDF()
    pdf.alias_nb_pages()
    parse_and_render(pdf, content)
    pdf.output(pdf_path)
    size = os.path.getsize(pdf_path)
    print(f"PDF generated: {pdf_path} ({size} bytes, {pdf.page_no()} pages)")

if __name__ == "__main__":
    main()
