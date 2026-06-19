import pdfplumber
from transformers import pipeline

# PDF에서 텍스트 추출 함수
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

# 요약 함수 (Hugging Face Transformers 활용)
def summarize_text(text, max_length=300):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
    return summary[0]['summary_text']

# 실행 예제
pdf_path = "example.pdf"  # 요약할 PDF 파일 경로
text = extract_text_from_pdf(pdf_path)

# 요약 적용
if len(text) > 500:  # 너무 짧은 경우 요약 생략
    summary = summarize_text(text)
    print("\n📌 요약 결과:\n", summary)
else:
    print("\n📌 PDF 내용이 너무 짧아서 요약이 필요하지 않음.")
