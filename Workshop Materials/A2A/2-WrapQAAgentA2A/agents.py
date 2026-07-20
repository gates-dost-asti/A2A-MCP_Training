import base64
from pathlib import Path

from gates_openai import create_response

class PolicyAgent:
    def __init__(self) -> None:
        with Path("../data/2026AnthemgHIPSBC.pdf").open("rb") as file:
            self.pdf_data = base64.standard_b64encode(file.read()).decode("utf-8")

    def answer_query(self, prompt: str) -> str:
        response = create_response(
            model = "gpt-4o-mini",
            input = [
                {
                    "role": "system",
                    "content": """You are an expert insurance agent designed to assist with
                    coverage queries. Use the provided documents to answer questions
                    about insurance policies. If the information is not available in
                    the documents, respond accordingly.
                    """
                },
                {
                    "role":"user",
                    "content": [
                        {
                            "type": "input_file",
                            "filename": "2026AnthemgHIPSBC.pdf",
                            "file_data": f"data:application/pdf;base64,{self.pdf_data}",
                        },
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )

        return response.output_text
