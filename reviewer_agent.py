import google.generativeai as genai
import config

class ReviewerAgent:
   
    def __init__(self):
        
        print("Initializing Reviewer Agent...")
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
            
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        self.model = genai.GenerativeModel(
            config.GEMINI_MODEL,
            generation_config={"temperature": 0.4}
        )
        print("Reviewer Agent ready.")

    def _create_prompt(self, spun_text: str) -> str:
        
        return (
            "You are a sharp, meticulous book editor with an eye for detail. "
            "Your task is to review the following draft. Please perform two actions:\n"
            "1. Provide a concise, bulleted list of 3-5 key suggestions for improvement. "
            "Focus on clarity, pacing, grammar, and style.\n"
            "2. After the list, provide the fully revised and polished version of the text "
            "that incorporates your own suggestions.\n\n"
            "Structure your response exactly as follows:\n"
            "**Review & Suggestions:**\n"
            "- Suggestion 1\n"
            "- Suggestion 2\n"
            "...\n\n"
            "**Revised Chapter:**\n"
            "[The full, edited text starts here]\n\n"
            "---\n"
            f"Draft to Review:\n{spun_text}"
        )

    def run(self, spun_text: str) -> tuple[str, str]:
        
        prompt = self._create_prompt(spun_text)
        
        print("Sending request to Gemini for review and refinement...")
        try:
            response = self.model.generate_content(prompt)
            full_response_text = response.text
            
            if "**Revised Chapter:**" in full_response_text:
                parts = full_response_text.split("**Revised Chapter:**", 1)
                feedback = parts[0].strip()
                revised_text = parts[1].strip()
                print("Successfully received and parsed the review.")
                return feedback, revised_text
            else:
                print("Warning: Reviewer output was not in the expected format.")
                return full_response_text, spun_text

        except Exception as e:
            print(f"An error occurred while communicating with the Gemini API: {e}")
            return None, None
