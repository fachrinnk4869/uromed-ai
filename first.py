import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import db
import google.generativeai as genai
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

load_dotenv()
app = FastAPI()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# simpan session + memory
active_sessions = {}


class SessionReq(BaseModel):
    session_id: str
    last_chat: str = None


@app.delete("/chat/{session_id}")
async def delete_history(session_id: str):
    db.delete_session(session_id)
    return {"message": f"History for session {session_id} deleted."}


@app.get("/chat/{session_id}")
async def get_chat(session_id: str):
    history = db.get_history_as_json(session_id)
    return {"session_id": session_id, "history": history}


@app.post("/start")
async def start_session(req: SessionReq):
    # tiap session punya memory sendiri
    if req.session_id not in active_sessions:
        active_sessions[req.session_id] = {
            "active": True,
            "last_chat": req.last_chat,
            "memory": db.get_memory(req.session_id),
        }
    else:
        active_sessions[req.session_id]["last_chat"] = req.last_chat

    return {"message": f"Session {req.session_id} started."}


@app.get("/analysis/ph")
async def analysis_ph():
    return {"status": "ok", "result": 6.5}


@app.get("/analysis/color")
async def analysis_color():
    return {"status": "ok", "result": "yellow"}


@app.get("/analysis/mass")
async def analysis_turbidity():
    return {"status": "ok", "result": "clear"}


@app.get("/analysis/velocity")
async def analysis_turbidity():
    return {"status": "ok", "result": 1000}


@app.post("/analysis/ai")
async def analysis_ai(request: Request):
    data = await request.json()
    print(data)
    context = {'ph_level': data.get("ph_level", ""),
               'color': data.get("color", ""), ''
               'mass': data.get("raw_sensor_data", "").get("mass", ""),
               'velocity': data.get("raw_sensor_data", "").get("velocity", ""),
               }
    prompt = f"Analyze the urine quality based on the following parameters:\nPH Level: {context['ph_level']}\nColor: {context['color']}\nMass: {context['mass']}\nVelocity: {context['velocity']}\nProvide a detailed analysis and suggestions for improvement if necessary. Just answer in short just one paragraph 4 sentence. use bahasa indonesia."
    response = model.generate_content(prompt, stream=False)
    return {"status": "ok", "result": response.text}


@app.get("/stream/{session_id}")
async def sse(session_id: str):
    async def event_stream(session_id: str):
        session = active_sessions.get(session_id)
        if not session or not session.get("active", False):
            yield "data: Session not active\n\n"
            return

        memory = session["memory"]
        user_input = session.get("last_chat", "Hello, who are you?")

        # tambahkan input user ke memory
        memory.chat_memory.add_message(HumanMessage(content=user_input))

        # ambil history percakapan
        history = memory.load_memory_variables({})["history"]

        # masukkan history ke prompt
        prompt = f"Conversation so far:\n{history}\nUser: {user_input}\nAI:"

        response = model.generate_content(prompt, stream=True)

        ai_response = ""
        for chunk in response:
            if chunk.text:
                ai_response += chunk.text
                yield f"data: {json.dumps(chunk.text)}\n\n"

        # simpan respon AI ke memory
        memory.chat_memory.add_message(AIMessage(content=ai_response))

        yield f"data: {json.dumps('[DONE]')}\n\n"

    return StreamingResponse(event_stream(session_id), media_type="text/event-stream")
