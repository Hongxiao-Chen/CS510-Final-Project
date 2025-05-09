import os
import csv
import ast

import numpy as np


class File:
    _id = 0

    def __init__(self, file_id=None, file_path=""):
        if file_id is None:
            self.file_id = self._id
            self.__class__._id += 1
        else:
            self.file_id = file_id

        self.file_path = file_path

    def to_list(self):
        return [self.file_id, self.file_path]


class EmbeddedFile(File):
    def __init__(self, file_id=None, file_path=np.ndarray):
        super().__init__(file_id=file_id, file_path=file_path)

    def to_list(self):
        return [self.file_id, np.array2string(self.file_path, separator=',', max_line_width=100000)]


def read_documents_csv(input_path, csv_name="documents.csv"):
    """
    Read documents.csv in target folder, and save to File
    Args:
        input_path: input folder
        csv_name: csv filename，documents.csv by default

    Returns:
        File list
    """
    csv_path = os.path.join(input_path, csv_name)

    documents = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            document = File(file_id=int(row[0]), file_path=row[1])
            documents.append(document)

    file.close()
    return documents


def read_embedded_documents(input_path, csv_name="documents.csv"):
    """
    Read documents.csv from 'embeddata' folder，and save to EmbeddedFile
    Args:
        input_path: input folder
        csv_name: csv filename，documents.csv by default

    Returns:
        EmbeddedFile list
    """
    csv_path = os.path.join(input_path, csv_name)

    documents = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            embed_file = EmbeddedFile(file_id=int(row[0]), file_path=np.array(ast.literal_eval(row[1])))
            documents.append(embed_file)

    file.close()
    return documents
