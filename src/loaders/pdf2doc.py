from src.loaders.file import File
from src.loaders.tags import load_tags
from src.loaders.doc2table import doc2table

from win32com import client


def pdf2docx(file_path: str):
    word = client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(file_path)
        new_path = file_path.replace('.pdf', '.docx')
        doc.SaveAs(new_path, FileFormat=16)
        doc.Close()
        return file_path.replace('.pdf', '.docx')
    except Exception as e:
        print(f"Error Converting PDF：{e}")
        return None
    finally:
        word.Quit()


if __name__ == "__main__":
    pdf_path = "D:\\CS\\CS510\\final-project\\data\\inputdata\\Test\\test.docx"
    tags = load_tags()
    # tb, tx = extract_pdf(pdf_path, tags)
    #
    # for i in tb:
    #     i.display()
    new_path = pdf2docx(pdf_path)
    print(new_path)
    file = File(file_path=new_path)
    tb, tx = doc2table(file, tags)
    for i in tb:
        i.display()

