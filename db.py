from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.schema import HumanMessage, AIMessage

DB_PATH = "chat_memory.db"

def get_memory(session_id: str):
    # pake SQLite untuk nyimpen chat history
    message_history = SQLChatMessageHistory(
        session_id=session_id,
        connection=f"sqlite:///{DB_PATH}"
    )
    memory = ConversationBufferWindowMemory(
        k=5,  # cuma ambil 5 pesan terakhir
        chat_memory=message_history,
        return_messages=True
    )
    return memory


def get_history_as_json(session_id: str):
    message_history = SQLChatMessageHistory(
        session_id=session_id,
        connection=f"sqlite:///{DB_PATH}"
    )
    history = []
    for msg in message_history.messages:
        history.append({
            "type": msg.type,      # "human" atau "ai"
            "content": msg.content # isi teks
        })
    return history

def delete_session(session_id: str):
    message_history = SQLChatMessageHistory(
        session_id=session_id,
        connection=f"sqlite:///{DB_PATH}"
    )
    message_history.clear()