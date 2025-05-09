import csv

from src.loaders.doc2table import doc2table
from src.loaders.tags import load_tags
from src.loaders.file import File

import os

objects_csv_name = "objects.csv"
documents_csv_name = "documents.csv"
tags_csv_name = "tags.csv"


def init_csv_files(document_path, object_path, tag_path):
    """
    Initialize csv file
    Args:
        document_path: document csv path
        object_path: object csv path
        tag_path: tag csv path
    """
    with open(document_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["file_id", "file_path"])
    file.close()

    with open(object_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["object_id", "file_id", "file_name", "position", "above", "below",
                         "title", "date", "content", "tags"])
    file.close()

    with open(tag_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["tag_id", "tag_name", "related_object_ids"])
    file.close()


def write_to_csv(elements, csv_path):
    with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for element in elements:
            row = element.to_list()
            writer.writerow(row)
    file.close()


def folder_to_csv(input_path):
    """
    Extract texts/tables from all files in the folder，and output a csv to data/outputdata with the same folder name
    Args:
        input_path: input path
    """
    folder_names = input_path.split('\\')  # os.splitext process '.'
    data_folder = ''
    for name in folder_names:
        data_folder += name + '\\'
        if name == 'data':
            break

    output_path = data_folder + 'outputdata\\' + folder_names[-1]
    os.makedirs(output_path, exist_ok=True)

    document_csv_path = os.path.join(output_path, documents_csv_name)
    object_csv_path = os.path.join(output_path, objects_csv_name)
    tag_csv_path = os.path.join(output_path, tags_csv_name)

    init_csv_files(document_csv_path, object_csv_path, tag_csv_path)

    file_list = []
    for files in os.walk(input_path):  # loop subfolders
        for file in files[2]:
            if os.path.splitext(file)[1].lower() == '.doc' or os.path.splitext(file)[1].lower() == '.docx':
                file = File(file_path=os.path.join(input_path, file))
                file_list.append(file)

    write_to_csv(file_list, document_csv_path)

    # load tags
    tags = load_tags()
    for file in file_list:
        print("Processing file：", file.file_path)
        tables, texts = doc2table(file, tags)
        elements = tables + texts
        write_to_csv(elements, object_csv_path)

    # write tags
    tags.to_csv(tag_csv_path)


if __name__ == "__main__":
    folder_to_csv("D:\\CS\\CS510\\final-project\\data\\inputdata\\Store")

