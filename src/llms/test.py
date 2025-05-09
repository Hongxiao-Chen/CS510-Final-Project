from zhipuai import ZhipuAI

client = ZhipuAI(api_key="")
response = client.chat.completions.create(
    model="glm-4-flash",
    messages=[
        {"role": "user", "content": "You are a highly skilled professional AI assistant specialized in Retrieval-Augmented Generation. Your primary goal is to help users by combining deep language understanding with relevant external knowledge retrieved from provided documents."},
    ],
)

print(response)