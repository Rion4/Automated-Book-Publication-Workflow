from playwright.sync_api import sync_playwright, Page
import config 

class ScraperAgent:
    
    def _calculate_reward_score(self, text: str) -> float:
   
        length_score = min((len(text) / 5000.0) * 100, 100)

        found_keywords = sum(1 for keyword in config.REWARD_KEYWORDS if keyword in text.lower())
        keyword_score = (found_keywords / len(config.REWARD_KEYWORDS)) * 100

        words = text.lower().split()
        noise_count = sum(1 for word in words if word in config.NOISE_WORDS)
        noise_ratio = (noise_count / len(words)) if len(words) > 0 else 0
        noise_score = noise_ratio * 1000 # Amplify the penalty

        # Combine scores using weights from the config file
        final_score = (
            (length_score * config.REWARD_WEIGHTS['length']) +
            (keyword_score * config.REWARD_WEIGHTS['keywords']) +
            (noise_score * config.REWARD_WEIGHTS['noise'])
        )
        
        # Ensure the score is capped between 0 and 100
        return max(0, min(100, final_score))

    def run(self, url: str) -> tuple[str, str, float]:
       
        print(f"Scraper Agent starting. Targeting URL: {url}")
        text_content = None
        screenshot_path = "screenshot.png"

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                
                print("Navigating to page...")
                page.goto(url, wait_until="networkidle", timeout=60000)

                print(f"Looking for content with selector: '{config.CONTENT_SELECTOR}'")
                content_element = page.locator(config.CONTENT_SELECTOR)
                
                content_element.wait_for(timeout=10000)

                text_content = content_element.inner_text()
                
                print("Content extracted. Taking screenshot...")
                page.screenshot(path=screenshot_path, full_page=True)
                
                browser.close()
                print(f"Screenshot saved to '{screenshot_path}'")

        except Exception as e:
            print(f"An error occurred during scraping: {e}")
            return None, None, 0.0

        if not text_content or text_content.isspace():
            print("Failed to extract any text content.")
            return None, None, 0.0
            
        print("Calculating quality score for the scraped text...")
        score = self._calculate_reward_score(text_content)
        print(f"Calculated Reward Score: {score:.2f} / 100")

        if score < config.REWARD_THRESHOLD:
            print(f"Warning: Score is below the threshold of {config.REWARD_THRESHOLD}.")
        
        return text_content, screenshot_path, score
