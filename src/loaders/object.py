from tabulate import tabulate
import pandas as pd
import numpy as np
import os
import csv
import ast


def arr2str(array: np.ndarray) -> str:
    return np.array2string(array, separator=',', max_line_width=100000)


class Object:
    _id = 0

    def __init__(self, object_id=None, file_id=0, file_name="", date=None,
                 position=0, above=None, below=None, title="", content="", tags=None):
        if date is None:
            date = set()

        if tags is None:
            tags = set()

        if object_id is None:
            self.object_id = self._id
            self.__class__._id += 1
        else:
            self.object_id = object_id

        self.file_id = file_id
        self.file_name = file_name
        self.date = date
        self.position = position
        self.above = above
        self.below = below
        self.title = title
        self.content = content
        self.tags = tags

    def display(self):
        print("Object ID:", self.object_id)
        print("File ID:", self.file_id)
        print("File Name:", self.file_name)
        print("Position:", self.position)
        print("Above:", self.above)
        print("Below:", self.below)
        print("Date:", self.date)

        if type(self.content) is dict:
            print("Title:", self.title)
            print("Content:\n", tabulate(pd.DataFrame(self.content), headers="keys", tablefmt="psql"))
        else:
            print("Content:\n", self.content)

        print("Tags:", self.tags)

    def to_str(self):
        """For LLM"""
        res = ""
        res += "Filename: " + self.file_name + '\n'
        res += "Preceding: " + self.above + '\n'
        res += "Succeeding: " + self.below + '\n'
        res += "Date: " + ','.join(self.date) + '\n'

        if type(self.content) is dict:
            res += "Table Name: " + self.title + '\n'
            res += "Table Content:\n" + str(self.content) + '\n'
        else:
            res += "Content:\n" + self.content + '\n'

        return res

    # def __repr__(self):
    #     return f"{self.object_id},{self.file_id},{self.position},
    #     {self.above},{self.below},{self.title},{self.content}"

    def to_list(self):
        """for csv conversion"""
        return [self.object_id, self.file_id, self.file_name, self.position,
                self.above, self.below, self.title, self.date, self.content, self.tags]


class EmbeddedObject:
    _id = 0

    def __init__(self, object_id=None, file_id=0, file_name=None, date=None,
                 position=0, above=None, below=None, title=None, content=None, tags=None, search_index=None):
        if date is None:
            date = set()

        if tags is None:
            tags = set()

        if object_id is None:
            self.object_id = self._id
            self.__class__._id += 1
        else:
            self.object_id = object_id

        self.file_id = file_id
        self.file_name = file_name
        self.date = date
        self.position = position
        self.above = above
        self.below = below
        self.title = title
        self.content = content
        self.tags = tags
        self.search_index = search_index

    def to_list(self):
        if type(self.content) is dict:
            content = self.content
        else:
            content = arr2str(self.content)

        return [self.object_id, self.file_id, arr2str(self.file_name), self.position,
                arr2str(self.above), arr2str(self.below),
                arr2str(self.title), self.date, content, self.tags, arr2str(self.search_index)]


def read_objects_csv(input_path, file_name="objects.csv"):
    """
    Read objects.csv in target folder
    Args:
        input_path: input folder
        file_name: csv filename, objects.csv by default

    Returns:
        Object list
    """
    csv_path = os.path.join(input_path, file_name)

    objects = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            if row[8].startswith('{') and row[8].endswith('}'):
                content = ast.literal_eval(row[8])  # dict
            else:
                content = row[8]  # text
            _object = Object(object_id=int(row[0]), file_id=int(row[1]), file_name=row[2],
                                  position=int(row[3]), above=row[4], below=row[5], title=row[6],
                                  date=ast.literal_eval(row[7]), content=content, tags=ast.literal_eval(row[9]))
            objects.append(_object)

    file.close()
    return objects


def read_embedded_objects(input_path, csv_name="objects.csv"):
    """
    Read objects.csv from 'embeddate' folder，and save to EmbeddedObject
    Args:
        input_path: input folder
        csv_name: csv filename，objects.csv by default

    Returns:
        EmbeddedObject list
    """
    csv_path = os.path.join(input_path, csv_name)

    objects = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)

        for row in reader:
            if row[8].startswith('{') and row[8].endswith('}'):
                content = ast.literal_eval(row[8])  # dict
            else:
                content = np.array(ast.literal_eval(row[8]))  # Embedding

            embed_object = EmbeddedObject(object_id=int(row[0]), file_id=int(row[1]), file_name=np.array(ast.literal_eval(row[2])),
                                          position=int(row[3]), above=np.array(ast.literal_eval(row[4])),
                                          below=np.array(ast.literal_eval(row[5])), title=np.array(ast.literal_eval(row[6])),
                                          date=ast.literal_eval(row[7]), content=content,
                                          tags=ast.literal_eval(row[9]), search_index=np.array(ast.literal_eval(row[10])))
            objects.append(embed_object)

    file.close()
    return objects
