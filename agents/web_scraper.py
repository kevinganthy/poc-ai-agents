from llama_index.core.tools import FunctionTool
from agents._agent import AbstractAgent
import os
import requests
from bs4 import BeautifulSoup
import html2text
from dotenv import load_dotenv

load_dotenv()

class WebScraperAgent(AbstractAgent):
    SERVICE_NAME = "web_scraper_agent"
    DESCRIPTION = "Useful for scraping web pages, parse content and answers some question about it."
    LLM_NAME = os.getenv("LLM_WEB_SCRAPER") or AbstractAgent.LLM_NAME
    
    def __init__(self):
        self.init_re_act_agent(
            [
                FunctionTool.from_defaults(fn=self.answer_question_about_webpage)
            ],
            self.get_llm(self.LLM_NAME)
        )
    
    def scrape_webpage(self, url: str) -> str:
        """
        Scrapes the content of a webpage and returns it as markdown.
        
        Args:
            url (str): The URL of the webpage to scrape.
            
        Returns:
            str: The content of the webpage in markdown format.
        """
        try:
            # Set a user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Make the request
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements that typically aren't part of the main content
            for element in soup(['script', 'style', 'iframe', 'nav', 'footer']):
                element.decompose()
            
            # Convert to markdown
            h2t = html2text.HTML2Text()
            h2t.ignore_links = False
            h2t.ignore_images = False
            h2t.body_width = 0  # No wrapping
            
            markdown_content = h2t.handle(str(soup))
            
            return markdown_content
            
        except Exception as e:
            return f"Error scraping webpage: {str(e)}"
    
    def answer_question_about_webpage(self, url: str, question: str) -> str:
        """
        Scrapes a webpage and answers a specific question about its content.
        
        Args:
            url (str): The URL of the webpage to analyze.
            question (str): The question to answer about the webpage content.
            
        Returns:
            str: An answer to the question based on the webpage content.
        """
        print("@@@@", question)
        try:
            # First scrape the webpage content
            content = self.scrape_webpage(url)
            
            if content.startswith("Error scraping webpage:"):
                return content
            
            # Construct a prompt for the LLM
            prompt = f"""Based on the following webpage content, please answer the question.
            
Webpage content:
{content[:10000]}  # Limit content to first 10000 chars to avoid token limits

Question: {question}

Answer:"""
            
            # Use the agent's LLM to generate an answer
            llm = self.get_llm(self.LLM_NAME)
            response = llm.complete(prompt)
            
            return f"Answer to '{question}':\n{response.text}"
            
        except Exception as e:
            return f"Error answering question: {str(e)}"