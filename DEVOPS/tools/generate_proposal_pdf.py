from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

input_md = 'DEVOPS/docs/proposal.md'
output_pdf = 'DEVOPS/docs/proposal.pdf'

# Read Markdown-like file and build PDF paragraphs
with open(input_md, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

styles = getSampleStyleSheet()
story = []

for line in lines:
    if line.strip() == '':
        story.append(Spacer(1, 6))
        continue
    if line.endswith('\n'):
        line = line.strip()
    # Simple markdown to style mapping
    if line.startswith('# '):
        story.append(Paragraph(line[2:].strip(), styles['Title']))
    elif line.startswith('## '):
        story.append(Paragraph(line[3:].strip(), styles['Heading2']))
    elif line.startswith('### '):
        story.append(Paragraph(line[4:].strip(), styles['Heading3']))
    elif line.startswith('---'):
        story.append(Spacer(1, 12))
    else:
        story.append(Paragraph(line.replace('  ', ''), styles['BodyText']))

    story.append(Spacer(1, 4))

# Build PDF
pdf = SimpleDocTemplate(output_pdf, pagesize=letter)
pdf.build(story)
print('Generated', output_pdf)
