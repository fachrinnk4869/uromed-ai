from typing import List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import google.generativeai as genai
import instructor
from pydantic import BaseModel, Field
from enum import Enum
load_dotenv()
app = FastAPI()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = instructor.from_gemini(
    client=genai.GenerativeModel(
        model_name="gemini-2.0-flash",
    ),
    mode=instructor.Mode.GEMINI_JSON,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Status(Enum):
    NORMAL = "normal"
    ABNORMAL = "abnormal"
    NEEDS_REVIEW = "needs_review"


class RiskDisease(BaseModel):
    """Model representing a potential disease or health risk."""
    name: str = Field(
        description="Name of the disease or health risk."
    )
    percentage: float = Field(
        description="Estimated likelihood (in percentage) of the disease or health risk."
    )
    based_on: str = Field(
        description="The specific urine quality parameters that indicate the presence of this disease or health risk. answer in short just one sentence"
    )
    description: str = Field(
        description="A brief description of the disease or health risk."
    )


class ResponseModel(BaseModel):
    """Response model for urine quality analysis."""
    analysis: str = Field(
        description="A detailed analysis of the urine quality based on the provided parameters."
    )
    solve_step: str = Field(
        description="Step-by-step suggestions for improving urine quality if any issues are detected.")
    risk_disease: List[RiskDisease] = Field(
        description="Potential diseases or health risks associated with the urine quality.")
    overall_status: Status = Field(
        description="Correctly assign one of the predefined roles to the user."
    )


prompt_raw = """Analyze the urine quality based on the following parameters:\n
PH Level: {ph_level} is the ph level of urine\n
Color: {color} is the color of urine\n
Mass: {mass} is mass of the urine in grams\n
Velocity: {velocity} is the velocity of urine flow in ml/second\n
Provide a detailed analysis and suggestions for improvement if necessary. Just answer in short just one paragraph 6 sentence. use bahasa indonesia."""


@app.post("/analysis/ai")
async def analysis_ai(request: Request):
    data = await request.json()
    print(data)
    context = {'ph_level': data.get("ph_level", ""),
               'color': data.get("color", ""), ''
               'mass': data.get("raw_sensor_data", "").get("mass", ""),
               'velocity': data.get("raw_sensor_data", "").get("velocity", ""),
               }
    prompt = f"{prompt_raw}".format(**context)
    # note that client.chat.completions.create will also work
    response = model.messages.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_model=ResponseModel,
    )
    return response


@app.get("/analysis/ph")
async def analysis_ph():
    return {"status": "ok", "result": 1}


@app.get("/analysis/color")
async def analysis_color():
    return {"status": "ok", "result": "red"}


@app.get("/analysis/mass")
async def analysis_turbidity():
    return {"status": "ok", "result": 5}


@app.get("/analysis/velocity")
async def analysis_turbidity():
    return {"status": "ok", "result": 1000}


@app.get("/")
async def root_call():
    return {"status": "ok"}

# This is important for Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
