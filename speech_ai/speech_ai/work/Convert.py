class convert_file:
    def convert_pdf_to_txt(self, file):
        import PyPDF2
        with open(file, 'rb') as file:
            # 创建 PDF 读取器对象
            reader = PyPDF2.PdfReader(file)
            # 获取 PDF 文件的页数
            num_pages = len(reader.pages)

            # 循环每一页
            for i in range(num_pages):
                # 读取每一页
                page = reader.pages[i]
                # 获取该页的文本
                text = page.extract_text ()
                # 将文本写入 txt 文件
                with open(f'{file}.txt', 'a') as txt_file:
                    txt_file.write(text)
    def word_to_txt(self, file):
        import docx
        #打开docx的文档并读入名为file的变量中
        file = docx.Document(file)
        #输入docx中的段落数，以检查是否空文档
        #将每个段落的内容都写进去txt里面
        with open(f'{file}.txt','w') as f:
            for para in file.paragraphs:
                f.write(para.text)