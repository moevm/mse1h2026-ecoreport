class PDFGenerator:
    """
    Класс для генерации PDF-документов.
    """
    async def generate_pdf(self, report_id: int) -> bytes:
        """
        Генерирует PDF-отчет по заданному идентификатору.

        :param report_id: Идентификатор отчета.
        :return: Содержимое PDF-файла в виде байтов.
        """
        return f"PDF content for report {report_id}".encode()
