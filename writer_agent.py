import google.generativeai as genai
import config

class WriterAgent:

    def __init__(self):
       
        print("Initializing Writer Agent...")
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        genai.configure(api_key=config.GOOGLE_API_KEY)

        self.model = genai.GenerativeModel(
            config.GEMINI_MODEL,
            generation_config={"temperature": 0.75}
        )
        print("Writer Agent ready.")

    def _create_prompt(self, original_text: str, human_feedback: str = None) -> str:
        
        base_prompt = (
            "You are a talented author specializing in modernizing classic literature. "
            "Your task is to rewrite the following chapter, preserving the core plot "
            "and character intentions, but infusing it with a more contemporary, "
            "dynamic, and descriptive prose. Make it engaging for a 21st-century reader.\n\n"
        )

        if human_feedback:
            # If feedback is provided, it's added to the prompt to guide the next iteration.
            # This is a key part of the human-in-the-loop process.
            feedback_prompt = (
                f"Please specifically address this feedback in your rewrite: '{human_feedback}'.\n\n"
            )
            return f"{base_prompt}{feedback_prompt}Original Chapter Text:\n---\n{original_text}"
        
        return f"{base_prompt}Original Chapter Text:\n---\n{original_text}"

    def run(self, original_text: str, human_feedback: str = None) -> str:
       
        prompt = self._create_prompt(original_text, human_feedback)
        
        print("Sending request to Gemini for text spinning...")
        try:
            response = self.model.generate_content(prompt)
            spun_text = response.text
            print("Successfully received spun text from the Writer Agent.")
            return spun_text
        except Exception as e:
            print(f"An error occurred while communicating with the Gemini API: {e}")
            # It's useful to see the prompt that caused the error for debugging.
            print(f"Failed prompt: {prompt[:300]}...")
            return None