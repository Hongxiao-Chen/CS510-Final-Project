import os
import gradio as gr
import pythoncom
import ast
import pandas as pd
import json
from tabulate import tabulate

from src.loaders.csv_converter import folder_to_csv
from src.embeddings.csv_embedding import embed_folder
from src.embeddings.baai import BAAIEmbeddings
from src.storages.faiss_search import FaissIdx
from src.llms.chatglm import ChatGLM
from src.llms.gemini import Gemini
from src.utils.hash import get_folder_hash
from src.utils.log import get_console_logger

logger = get_console_logger('Frontend')

input_data_path = "..\\..\\data\\inputdata"
output_data_path = "..\\..\\data\\outputdata"
embedded_data_path = "..\\..\\data\\embeddata"

with open("../../config.json") as f:
    config = json.load(f)
    ChatGLM_api_key = config["ChatGLM_api_key"]
    Gemini_api_key = config["Gemini_api_key"]

# TODO: config part, modify before running on a new machine
model = BAAIEmbeddings("../models/bge-base-en-v1.5") # change it into "BAAI/bge-base-en-v1.5" on new machine
faiss_retriever = FaissIdx(model)
chatglm_4_flash = ChatGLM(api_key=ChatGLM_api_key, model="glm-4-flash")
chatglm_z1_flash = ChatGLM(api_key=ChatGLM_api_key, model="glm-z1-flash")
gemini_2_flash = Gemini(api_key=Gemini_api_key, model="gemini-2.0-flash")

startup_prompt = [
        {"role": "user", "content": "You are a highly skilled professional AI assistant specialized in Retrieval-Augmented Generation. Your primary goal is to help users by combining deep language understanding with relevant external knowledge retrieved from provided documents."},
        {"role": "assistant", "content": "Sure, please send me your query and data."},
    ]



def list_data_dirs(path=input_data_path):
    """list all folder names under 'data/inputdata', for knowledge base name"""
    dirs = [entry.name for entry in os.scandir(path) if entry.is_dir()]
    return dirs


def load_kg(kg_name):
    """
    load knowledge base，first extract tables/texts to outputdata，then proceed embedding and save to embeddata
    Args:
        kg_name: folder name，should be under data/inputdata
    """
    pythoncom.CoInitialize()
    # Init path
    input_kg_path = os.path.abspath(os.path.join(input_data_path, kg_name))
    output_kg_path = os.path.abspath(os.path.join(output_data_path, kg_name))
    embed_kg_path = os.path.abspath(os.path.join(embedded_data_path, kg_name))
    # Check if knowledge base is updated
    if os.path.exists(os.path.join(embed_kg_path, "hash.txt")):  # No update, using original embeddings
        curr_hash = get_folder_hash(input_kg_path)
        stored_hash = open(os.path.join(embed_kg_path, "hash.txt"), "r").read()

        if curr_hash == stored_hash:
            faiss_retriever.add_folder(output_kg_path, embed_kg_path)
            pythoncom.CoUninitialize()
            return "Successfully loaded " + kg_name + "（no update to knowledge base, using cache）"
    else:  # Updated, embedding again
        # Convert to CSV
        folder_to_csv(input_kg_path)
        # Embedding
        embed_folder(model, output_kg_path)
        # Load to Faiss
        faiss_retriever.add_folder(output_kg_path, embed_kg_path)
        # Release pywin32
        pythoncom.CoUninitialize()
        # Update hash
        with open(os.path.join(embed_kg_path, "hash.txt"), 'w') as file:
            file.write(get_folder_hash(input_kg_path))
        return "Successfully loaded " + kg_name + "（knowledge base updated）"


def clear_session():
    """Clean history log"""
    return [], [], ""


def chat_bot_response(message, top_k, history, search, llm):
    """Accept user input，if is 'dict', convert to table，else hand to 'predict' method to search"""
    logger.info("Using " + llm)
    if llm == "ChatGLM4-Flash":
        llm_model = chatglm_4_flash
    elif llm == "Gemini-2.0-Flash":
        llm_model = gemini_2_flash
    elif llm == "ChatGLM-Z1-Flash":
        llm_model = chatglm_z1_flash
    else:
        llm_model = None

    if history is None:
        history = []
    if message.startswith("{") and message.endswith("}"):
        table = tabulate(pd.DataFrame(ast.literal_eval(message)), headers="keys", tablefmt="pipe", showindex=False)
        history.append((message, table))
        return history, history, "", search
    else:
        return predict(message, top_k, history, llm_model)


def predict(message, top_k, history, llm):
    """
    Send message to LLM and FAISS
    Args:
        message: user input
        top_k: top-k hyperparameter
        history: gr.State() search history

    Returns:
        (chatbot, gr.State() history, ""(Reset chatbox), FAISS history)
    """
    if history is None:
        history = []
    top_res = faiss_retriever.search_doc(message, k=top_k)

    query = "Please read the following documents：\n"
    search_res = ""
    for i in range(len(top_res)):
        search_res += f"--------No.{i+1} Search Result--------\n"
        search_res += next(iter(top_res[i])) + "\n"
    query += "Answer this according to the documents：" + message + "\n"

    if llm is None:
        answer = "LLM not loaded，only returning FAISS results"
    else:
        logger.info("To LLM: " + query + search_res)
        answer, _ = llm.answer(query + search_res, startup_prompt)
    history.append((message, answer))
    return history, history, "", search_res


with gr.Blocks() as demo:
    gr.Markdown("""<h1><center>Tabular RAG</center></h1>
        <center><font size=3>
        </center></font>
        """)
    state = gr.State()

    with gr.Row():
        with gr.Column(scale=1):
            embedding_model = gr.Dropdown(
                [
                    "bge-base-en-v1.5",
                ],
                label="Embedding Model",
                value="bge-base-en-v1.5")

            large_language_model = gr.Dropdown(
                [
                    "ChatGLM4-Flash",
                    "Gemini-2.0-Flash",
                    "ChatGLM-Z1-Flash"
                ],
                label="Large Language Model",
                value="Gemini-2.0-Flash")

            top_k = gr.Slider(1,
                              20,
                              value=4,
                              step=1,
                              label="Top-K documents",
                              interactive=True)

            kg_name = gr.Radio(list_data_dirs(input_data_path),
                               label="Knowledge base",
                               value=None,
                               info="To use knowledge base for questions, please load first",
                               interactive=True)

            set_kg_btn = gr.Button("Load knowledge base")

            kg_status = gr.Textbox(label="Knowledge base status", value="Not loaded")

        with gr.Column(scale=4):
            with gr.Row():
                chatbot = gr.Chatbot(label='Tabular RAG')
            with gr.Row():
                message = gr.Textbox(label='Query')
            with gr.Row():
                clear_history = gr.Button("🧹Clean history")
                send = gr.Button("🚀Send")
        with gr.Column(scale=2):
            search = gr.Textbox(label='Search results')

        # ============= Triggers =============
        set_kg_btn.click(  # show_progress=True
            load_kg,
            inputs=[kg_name],  # for switching models
            outputs=[kg_status],
            show_progress="full")

        # send
        send.click(chat_bot_response,
                   inputs=[message, top_k, state, search, large_language_model],
                   outputs=[chatbot, state, message, search])

        # clean history
        clear_history.click(fn=clear_session,
                            inputs=[],
                            outputs=[chatbot, state, search],
                            queue=False)

        # enter key
        message.submit(chat_bot_response,
                       inputs=[message, top_k, state, search, large_language_model],
                       outputs=[chatbot, state, message, search])


demo.launch(
    show_error=True,
    debug=True,
)
