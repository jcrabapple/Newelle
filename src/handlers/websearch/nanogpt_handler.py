import requests
import json
from typing import Callable
from .websearch import WebSearchHandler
from ...handlers import ErrorSeverity
import time
import logging

logging.basicConfig(level=logging.INFO)


class NanoGPTWebSearchHandler(WebSearchHandler):
    """Web Search handler for NanoGPT API"""
    key = "nanogpt"
    
    def __init__(self, settings, path):
        super().__init__(settings, path)
        
    def query(self, keywords: str) -> tuple[str, list]:
        """Perform a web search using NanoGPT API
        
        Args:
            keywords: the search query
            
        Returns:
            - str: the search results formatted for the LLM
            - list: the list of source URLs
        """


        retries = 3
        backoff_factor = 2

        for i in range(retries):
            try:
                # Get API settings
                api_key = self.get_setting("api", False)
                endpoint = self.get_setting("endpoint", "https://nano-gpt.com/api/web")
                search_type = self.get_setting("search_type", "standard")
                
                if not api_key:
                    self.throw("NanoGPT API key is not configured", ErrorSeverity.WARNING)
                    return "", []
                
                # Make the API request
                url = endpoint
                headers = {
                    "x-api-key": api_key,
                    "Content-Type": "application/json"
                }
                logging.info(f"Request headers: {headers}")
                logging.info(f"Request payload: {data}")

                response = requests.post(url, headers=headers, json=data, timeout=30)
                
                logging.info(f"Response status code: {response.status_code}")
                logging.info(f"Response content: {response.text}")

                response.raise_for_status()
                
                result = response.json()
                
                # Format the results
                sources = []
                formatted_results = []
                
                if "results" in result:
                    for item in result["results"]:
                        if "url" in item:
                            sources.append(item["url"])
                        if "title" in item and "snippet" in item:
                            formatted_results.append(f"{item['title']}: {item['snippet']}")
                
                return "\n".join(formatted_results), sources
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    self.throw(f"Endpoint not found: {url}", ErrorSeverity.ERROR)
                    return "", []
                if i < retries - 1:
                    sleep_time = backoff_factor ** i
                    logging.warning(f"Request failed with {e}. Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    self.throw(f"Error performing NanoGPT web search: {str(e)}", ErrorSeverity.WARNING)
                    return "", []
            except Exception as e:
                self.throw(f"Error performing NanoGPT web search: {str(e)}", ErrorSeverity.WARNING)
                return "", []
        return "", []
    
    def query_streaming(self, keywords: str, add_website: Callable) -> tuple[str, list]:
        """Perform a web search in streaming mode
        
        Args:
            keywords: the search query
            add_website: function to add website information
            
        Returns:
            - str: the search results formatted for the LLM
            - list: the list of source URLs
        """


        retries = 3
        backoff_factor = 2

        for i in range(retries):
            try:
                # Get API settings
                api_key = self.get_setting("api", False)
                endpoint = self.get_setting("endpoint", "https://nano-gpt.com/api/web")
                search_type = self.get_setting("search_type", "standard")
                
                if not api_key:
                    self.throw("NanoGPT API key is not configured", ErrorSeverity.WARNING)
                    return "", []
                
                # Make the API request
                url = endpoint
                headers = {
                    "x-api-key": api_key,
                    "Content-Type": "application/json"
                }
                
                data = {
                    "query": keywords,
                    "type": search_type
                }

                logging.info(f"Making web search request to: {url}")
                logging.info(f"Request headers: {headers}")
                logging.info(f"Request payload: {data}")
                
                response = requests.post(url, headers=headers, json=data, timeout=30)

                logging.info(f"Response status code: {response.status_code}")
                logging.info(f"Response content: {response.text}")
                
                response.raise_for_status()
                
                result = response.json()
                
                # Format the results and add websites
                sources = []
                formatted_results = []
                
                if "results" in result:
                    for item in result["results"]:
                        if "url" in item:
                            sources.append(item["url"])
                            # Add website to the UI
                            title = item.get("title", "Unknown")
                            add_website(title, item["url"], None)
                        if "title" in item and "snippet" in item:
                            formatted_results.append(f"{item['title']}: {item['snippet']}")
                
                return "\n".join(formatted_results), sources
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    self.throw(f"Endpoint not found: {url}", ErrorSeverity.ERROR)
                    return "", []
                if i < retries - 1:
                    sleep_time = backoff_factor ** i
                    logging.warning(f"Request failed with {e}. Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    self.throw(f"Error performing NanoGPT web search: {str(e)}", ErrorSeverity.WARNING)
                    return "", []
            except Exception as e:
                self.throw(f"Error performing NanoGPT web search: {str(e)}", ErrorSeverity.WARNING)
                return "", []
        return "", []
    
    def get_extra_settings(self) -> list:
        """Get extra settings for NanoGPT web search"""
        return [
            {
                "key": "api",
                "title": "API Key",
                "description": "NanoGPT API key for web search",
                "type": "entry",
                "default": "",
                "password": True
            },
            {
                "key": "endpoint",
                "title": "Web Search Endpoint",
                "description": "NanoGPT API endpoint for web search",
                "type": "entry",
                "default": "https://nano-gpt.com/api/web"
            },
            {
                "key": "search_type",
                "title": "Search Type",
                "description": "Type of web search to perform",
                "type": "combo",
                "default": "standard",
                "values": [
                    ("Standard Search", "standard"),
                    ("Deep Search", "deep")
                ]
            },
            {
                "key": "link_scraping",
                "title": "Enable Link Scraping",
                "description": "Enable or disable link scraping",
                "type": "toggle",
                "default": False
            },
            {
                "key": "scraping_endpoint",
                "title": "Scraping Endpoint",
                "description": "API endpoint for link scraping",
                "type": "entry",
                "default": "https://nano-gpt.com/api/v1/scrape"
            },
            {
                "key": "youtube_summarization",
                "title": "Enable YouTube Summarization",
                "description": "Enable or disable YouTube summarization",
                "type": "toggle",
                "default": False
            },
            {
                "key": "youtube_summarization_endpoint",
                "title": "YouTube Summarization Endpoint",
                "description": "API endpoint for YouTube summarization",
                "type": "entry",
                "default": "https://nano-gpt.com/api/v1/summarize-youtube"
            }
        ]
    
    def supports_streaming_query(self) -> bool:
        return True

    def scrape_link(self, url: str) -> str:
        """Scrape a link using NanoGPT API
        
        Args:
            url: the URL to scrape
            
        Returns:
            The scraped content
        """
        if not self.get_setting("link_scraping", False):
            self.throw("Link scraping is not enabled", ErrorSeverity.WARNING)
            return ""
        
        try:
            # Get API settings
            api_key = self.get_setting("api", False)
            endpoint = self.get_setting("scraping_endpoint", "https://nano-gpt.com/api/v1/scrape")
            
            if not api_key:
                self.throw("NanoGPT API key is not configured", ErrorSeverity.WARNING)
                return ""
            
            # Make the API request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "url": url
            }
            
            response = requests.post(endpoint, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if "content" in result:
                return result["content"]
            else:
                return ""
            
        except Exception as e:
            self.throw(f"Error scraping link: {str(e)}", ErrorSeverity.WARNING)
            return ""

    def summarize_youtube(self, url: str) -> str:
        """Summarize a YouTube video using NanoGPT API
        
        Args:
            url: the YouTube video URL
            
        Returns:
            The summary of the video
        """
        if not self.get_setting("youtube_summarization", False):
            self.throw("YouTube summarization is not enabled", ErrorSeverity.WARNING)
            return ""
        
        try:
            # Get API settings
            api_key = self.get_setting("api", False)
            endpoint = self.get_setting("youtube_summarization_endpoint", "https://nano-gpt.com/api/v1/summarize-youtube")
            
            if not api_key:
                self.throw("NanoGPT API key is not configured", ErrorSeverity.WARNING)
                return ""
            
            # Make the API request
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "url": url
            }
            
            response = requests.post(endpoint, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            
            if "summary" in result:
                return result["summary"]
            else:
                return ""
            
        except Exception as e:
            self.throw(f"Error summarizing YouTube video: {str(e)}", ErrorSeverity.WARNING)
            return ""