import numpy as np

import os
import csv
import ast
import json

default_local_path = os.path.join(os.path.dirname(__file__), "local_tags.json")


class Tags:
    def __init__(self):
        self.tags_dict = {}

    def add_tag(self, tag_name, related_object_id=None):
        if related_object_id is not None:  # given id
            if tag_name in self.tags_dict:
                self.tags_dict[tag_name].add(related_object_id)
            else:  # is date
                new_set = set()
                new_set.add(related_object_id)
                self.tags_dict[tag_name] = new_set
        else:  # no id
            if tag_name in self.tags_dict:
                return
            else:
                self.tags_dict[tag_name] = set()

    def add_tags(self, tag_name, related_object_ids):
        self.tags_dict[tag_name] = related_object_ids

    def is_in(self, tag_name):
        return tag_name in self.tags_dict

    def to_csv(self, csv_path):
        with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)

            id = 0
            for tag in self.tags_dict:
                related_object_ids = self.tags_dict[tag]
                if related_object_ids != set():
                    row = [id, tag, related_object_ids]
                    writer.writerow(row)
                    id += 1
        file.close()


class EmbeddedTag:
    _id = 0

    def __init__(self, tag_name: np.ndarray, related_object_ids: set, tag_id=None):
        if tag_id is None:
            self.tag_id = self._id
            self.__class__._id += 1
        else:
            self.tag_id = tag_id
        self.tag_name = tag_name
        self.related_object_ids = related_object_ids

    def to_list(self):
        return [self.tag_id, np.array2string(self.tag_name, separator=',', max_line_width=100000),
                self.related_object_ids]


def read_embedded_tags(input_path, csv_name="tags.csv"):
    """
    Read tags.csv from 'embeddata'，and store to EmbeddedTag
    Args:
        csv_name: csv name，tags.csv by default
        input_path: input folder

    Returns:
        EmbeddedTag list
    """
    csv_path = os.path.join(input_path, csv_name)

    tags = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)  # skip headers

        for row in reader:
            _tag = EmbeddedTag(tag_id=int(row[0]), tag_name=np.array(ast.literal_eval(row[1])),
                                    related_object_ids=ast.literal_eval(row[2]))
            tags.append(_tag)

    file.close()
    return tags


def load_tags_from_local(path):
    tags = read_tags(path)
    return tags


def load_tags(local_path=default_local_path):
    """
    Load tags from given path
    Args:
        local_path: local tag path

    Returns:
        Tag set
    """
    tags = []
    local_tags = load_tags_from_local(local_path)
    for i in local_tags:
        tags.append(i.strip())

    # Store Tags to save/join
    output_tags = Tags()
    for tag in tags:
        output_tags.add_tag(tag)

    return output_tags


def read_tags(path):
    with open(path, 'r', encoding='utf-8') as file:
        tags = json.load(file)

    file.close()
    return tags


def write_tags(path, content):
    json_str = json.dumps(content, ensure_ascii=False)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(json_str)

    file.close()


def read_tags_csv(input_path, file_name="tags.csv"):
    """
    Read tags.csv in target folder
    Args:
        input_path: folder to read
        file_name: csv filename

    Returns:
        Object list
    """
    csv_path = os.path.join(input_path, file_name)

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)

        tags = Tags()
        for row in reader:
            related_object_ids = ast.literal_eval(row[2])
            tags.add_tags(tag_name=row[1], related_object_ids=related_object_ids)

    file.close()
    return tags


if __name__ == "__main__":
    tags = load_tags()
    for i in tags.tags_dict:
        print(i, tags.tags_dict[i])
