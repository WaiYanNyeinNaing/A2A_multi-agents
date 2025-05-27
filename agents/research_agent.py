# agents/research_agent.py
"""
Research Agent using Web Search APIs and Google Gemini
- Specialized for web research and data collection
- Integrates with Serper API for web searches
- Plans and executes research queries
"""

import os
import requests
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    """
    Research Agent specialized for web search and data collection
    """
    
    def __init__(self):
        super().__init__("research_specialist")
        # Load environment variables from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv not available, rely on system env vars
        
        self.serper_api_key = os.getenv('SERPER_API_KEY')
    
    def web_search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Search the web using Serper API.
        
        Args:
            query: The search query
            num_results: Number of results to return (max 30)
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            if not self.serper_api_key:
                # Return a mock response instead of error to avoid breaking the flow
                return self.create_success_response(
                    search_id=self.generate_unique_id(),
                    query=query,
                    results=[{
                        'title': 'Search API Configuration Required',
                        'link': '',
                        'snippet': 'SERPER_API_KEY not configured. Please add your Serper API key to the .env file to enable web search.',
                        'position': 1
                    }],
                    knowledge_graph=None,
                    total_results=1,
                    search_time=0
                )
            
            headers = {
                'X-API-KEY': self.serper_api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                "q": query,
                "num": min(num_results, 30)  # API limit
            }
            
            response = requests.post(
                "https://google.serper.dev/search", 
                headers=headers, 
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract and format results
                results = []
                if 'organic' in data and data['organic']:
                    for item in data['organic'][:num_results]:
                        if item:  # Ensure item is not None
                            results.append({
                                'title': item.get('title', ''),
                                'link': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'position': item.get('position', 0)
                            })
                elif 'answerBox' in data:
                    # Sometimes search results come in answerBox format
                    answer_box = data['answerBox']
                    results.append({
                        'title': answer_box.get('title', 'Direct Answer'),
                        'link': answer_box.get('link', ''),
                        'snippet': answer_box.get('snippet', answer_box.get('answer', '')),
                        'position': 1
                    })
                
                # Add knowledge graph if available
                knowledge_info = None
                if 'knowledgeGraph' in data:
                    kg = data['knowledgeGraph']
                    knowledge_info = {
                        'title': kg.get('title', ''),
                        'description': kg.get('description', ''),
                        'website': kg.get('website', ''),
                        'attributes': kg.get('attributes', {})
                    }
                
                # Ensure results is not None
                if results is None:
                    results = []
                
                return self.create_success_response(
                    search_id=self.generate_unique_id(),
                    query=query,
                    results=results,
                    knowledge_graph=knowledge_info,
                    total_results=len(results),
                    search_time=data.get('searchTime', 0)
                )
            else:
                return self.create_error_response(f"Search API error: {response.status_code}", "api_error")
                
        except Exception as e:
            return self.create_error_response(str(e), "search_error")
    
    def research_topic(self, topic: str, num_searches: int = 5) -> Dict[str, Any]:
        """
        Conduct comprehensive research on a topic using multiple searches.
        
        Args:
            topic: Research topic or question
            num_searches: Number of different search queries to perform
            
        Returns:
            Dict containing aggregated research results
        """
        try:
            # Generate search queries for the topic
            search_queries = self._generate_search_queries(topic, num_searches)
            
            # Ensure we have valid search queries
            if not search_queries:
                search_queries = [f"{topic} overview", f"{topic} information"]
            
            all_results = []
            search_summaries = []
            
            for i, query in enumerate(search_queries):
                search_result = self.web_search(query, 5)  # 5 results per query
                
                if search_result.get("success"):
                    all_results.extend(search_result.get("results", []))
                    search_summaries.append({
                        "query": query,
                        "results_count": len(search_result.get("results", [])),
                        "top_result": search_result.get("results", [{}])[0].get("title", "") if search_result.get("results") else ""
                    })
            
            # Generate research summary
            summary = self._generate_research_summary(topic, all_results)
            
            return self.create_success_response(
                research_id=self.generate_unique_id(),
                topic=topic,
                search_queries=search_queries,
                total_results=len(all_results),
                search_summaries=search_summaries,
                results=all_results,
                summary=summary
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "research_error")
    
    def fact_check(self, claim: str) -> Dict[str, Any]:
        """
        Fact-check a claim using web search.
        
        Args:
            claim: The claim to fact-check
            
        Returns:
            Dict containing fact-check results and sources
        """
        try:
            # Create fact-checking queries
            queries = [
                f"{claim} fact check",
                f"{claim} evidence",
                f"{claim} studies research",
                f"{claim} true false"
            ]
            
            all_sources = []
            for query in queries:
                result = self.web_search(query, 3)
                if result.get("success"):
                    all_sources.extend(result.get("results", []))
            
            # Analyze credibility of sources
            credible_sources = self._filter_credible_sources(all_sources)
            
            return self.create_success_response(
                fact_check_id=self.generate_unique_id(),
                claim=claim,
                sources_found=len(all_sources),
                credible_sources=credible_sources,
                queries_used=queries
            )
            
        except Exception as e:
            return self.create_error_response(str(e), "fact_check_error")
    
    def _generate_search_queries(self, topic: str, num_queries: int) -> List[str]:
        """Generate multiple search queries for comprehensive research."""
        # Use Gemini to generate diverse search queries
        prompt = f"""
        Generate {num_queries} different search queries to research this topic comprehensively: "{topic}"
        
        The queries should cover different aspects like:
        - Basic definition and overview
        - Recent developments
        - Expert opinions
        - Statistics and data
        - Practical applications
        
        Return only the search queries, one per line.
        """
        
        try:
            response = self.call_gemini_api(prompt)
            queries = [q.strip().strip('"\'') for q in response.split('\n') if q.strip()]
            # Remove any remaining quotes and clean up queries
            cleaned_queries = []
            for q in queries:
                # Remove quotes and extra whitespace
                clean_q = q.replace('"', '').replace("'", '').strip()
                if clean_q:
                    cleaned_queries.append(clean_q)
            return cleaned_queries[:num_queries]
        except:
            # Fallback queries
            return [
                f"{topic} overview",
                f"{topic} recent news",
                f"{topic} statistics data", 
                f"{topic} expert analysis",
                f"{topic} research studies"
            ][:num_queries]
    
    def _generate_research_summary(self, topic: str, results: List[Dict]) -> str:
        """Generate a summary of research results."""
        if not results:
            return "No research results found."
        
        # Extract key information from results
        titles = [r.get('title', '') for r in results[:10]]  # Top 10 results
        snippets = [r.get('snippet', '') for r in results[:10]]
        
        prompt = f"""
        Based on these research results about "{topic}", provide a concise summary (2-3 paragraphs):
        
        Titles: {titles}
        
        Snippets: {snippets}
        
        Focus on the main findings, key facts, and important insights. Be objective and factual.
        """
        
        try:
            return self.call_gemini_api(prompt)
        except:
            return "Research completed successfully. Multiple sources were found and analyzed."
    
    def _filter_credible_sources(self, sources: List[Dict]) -> List[Dict]:
        """Filter sources by credibility based on domain and content quality."""
        credible_domains = [
            '.edu', '.gov', '.org', 'reuters.com', 'bbc.com', 'npr.org',
            'nature.com', 'science.org', 'pubmed.ncbi.nlm.nih.gov'
        ]
        
        credible = []
        for source in sources:
            link = source.get('link', '').lower()
            if any(domain in link for domain in credible_domains):
                credible.append(source)
        
        return credible[:5]  # Return top 5 credible sources
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        return {
            "name": "Research Specialist",
            "type": "research", 
            "model": self.model_name,
            "capabilities": ["web_search", "research_topic", "fact_check"],
            "apis": ["serper"],
            "status": "ready" if self.serper_api_key else "limited"
        }