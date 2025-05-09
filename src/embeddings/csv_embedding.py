import csv
import os

from tqdm import tqdm

from src.loaders.file import File, EmbeddedFile, read_documents_csv
from src.loaders.object import Object, EmbeddedObject, read_objects_csv
from src.loaders.tags import Tags, EmbeddedTag, read_tags_csv
from src.embeddings.baai import BAAIEmbeddings


def documents_embedding(model: BAAIEmbeddings, documents: list[File]):
    """
    Save Embeddings of File to EmbeddedFile
    Args:
        model: embedding model
        documents: File list

    Returns:
        EmbeddedFile list
    """
    embed_documents = []
    for doc in tqdm(documents):
        embed_doc = EmbeddedFile(file_id=doc.file_id, file_path=model.embed_query(doc.file_path))
        embed_documents.append(embed_doc)

    return embed_documents


def objects_embedding(model: BAAIEmbeddings, objects: list[Object]):
    """
    Save Embeddings of Object to EmbeddedObject，tags(date+table name+tags) for tables，content for text
    Args:
        model: embedding model
        objects: Object list

    Returns:
        EmbeddedObject list
    """
    embed_objects = []
    for object in tqdm(objects):
        if type(object.content) is dict:
            embed_list = model.embed_documents([object.file_name, object.above, object.below, object.title,
                                                ','.join(object.date) + "[SEP]" + object.title + "[SEP]" + ','.join(
                                                    object.tags)])
            embed_object = EmbeddedObject(object_id=object.object_id, file_id=object.file_id,
                                          file_name=embed_list[0],
                                          position=object.position, above=embed_list[1], below=embed_list[2],
                                          title=embed_list[3], date=object.date, content=object.content,
                                          tags=object.tags, search_index=embed_list[4])
        else:
            embed_list = model.embed_documents([object.file_name, object.above, object.below, object.title, object.content])
            embed_object = EmbeddedObject(object_id=object.object_id, file_id=object.file_id,
                                          file_name=embed_list[0],
                                          position=object.position, above=embed_list[1], below=embed_list[2],
                                          title=embed_list[3], date=object.date, content=embed_list[4],
                                          tags=object.tags, search_index=embed_list[4])

        embed_objects.append(embed_object)
    return embed_objects


def tags_embedding(model: BAAIEmbeddings, tags: Tags):
    """
    Save Embeddings of Tags to EmbeddedTags
    Args:
        model: embedding model
        tags: Tags

    Returns:
        EmbeddedTags
    """
    embed_tags = []
    for tag in tqdm(tags.tags_dict):
        embed_tag = model.embed_query(tag)
        embed_tags.append(EmbeddedTag(tag_name=embed_tag, related_object_ids=tags.tags_dict[tag]))
    return embed_tags


def init_embed_folder(path: str):
    """
    Initialize embeddata folder
    Args:
        path: original path

    Returns:
        New folder path
    """
    folder_names = path.split('\\')
    data_folder = ''
    for name in folder_names:
        data_folder += name + '\\'
        if name == 'data':
            break
    output_path = data_folder + 'embeddata\\' + folder_names[-1]
    os.makedirs(output_path, exist_ok=True)
    return output_path


def embed_documents_to_csv(model, input_path):
    docs = read_documents_csv(input_path)
    output_path = init_embed_folder(input_path)
    # File Embedding
    embedded_docs = documents_embedding(model, docs)

    csv_path = os.path.join(output_path, "documents.csv")
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["file_id, file_path"])

        for doc in embedded_docs:
            writer.writerow(doc.to_list())
    file.close()
    return embedded_docs


def embed_objects_to_csv(model, input_path):
    objects = read_objects_csv(input_path)
    output_path = init_embed_folder(input_path)
    # Objects Embedding
    embedded_objects = objects_embedding(model, objects)

    csv_path = os.path.join(output_path, "objects.csv")
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["object_id", "file_id", "file_name", "position", "above", "below", "title",
                         "date", "content", "tags", "search_index"])

        for obj in embedded_objects:
            writer.writerow(obj.to_list())
    file.close()
    return embedded_objects


def embed_tags_to_csv(model, input_path):
    tags = read_tags_csv(input_path)
    output_path = init_embed_folder(input_path)
    # Tags Embedding
    embedded_tags = tags_embedding(model, tags)

    csv_path = os.path.join(output_path, "tags.csv")
    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["tag_id, tag_name, related_object_ids"])

        for obj in embedded_tags:
            writer.writerow(obj.to_list())
    file.close()
    return embedded_tags


def embed_folder(model, input_path):
    print("Embedding documents.csv")
    embed_documents_to_csv(model, input_path)
    print("Embedding objects.csv")
    embed_objects_to_csv(model, input_path)
    print("Embedding tags.csv")
    embed_tags_to_csv(model, input_path)


if __name__ == "__main__":
    model = BAAIEmbeddings()
    embed_folder(model, "D:\\CS\\CS510\\final-project\\data\\outputdata\\Store")
