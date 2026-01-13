from groq import Groq
import requests
import json
from datetime import datetime
import os
import streamlit as st
import logging
import sys

# Configure logging with centralized config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/research_assistant.log')
    ]
)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger(__name__)

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize client only if API key is available
# (will be initialized later by web_app.py with proper error handling)
client = None
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)

def search_topic(query):
    """Search and return relevant info with citations"""
    logger.info(f"Starting search for query: {query}")
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    try:
        # Add user agent to improve response quality
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=5, headers=headers)
        data = response.json()
        
        results = []
        citations = []
        
        # Get abstract
        if data.get('AbstractText'):
            results.append(data['AbstractText'])
            if data.get('AbstractSource'):
                citations.append(f"Source: {data['AbstractSource']}")
        
        # Get related topics
        for i, topic in enumerate(data.get('RelatedTopics', [])[:5], 1):
            if 'Text' in topic:
                results.append(f"[{i}] {topic['Text']}")
                if 'FirstURL' in topic:
                    citations.append(f"[{i}] {topic['FirstURL']}")
        
        return_data = {
            "content": "\n".join(results) if results else "No information found",
            "citations": citations if citations else []
        }
        logger.info(f"Search successful for '{query}': found {len(results)} results and {len(citations)} citations")
        return return_data
    except Exception as e:
        logger.error(f"Search failed for query '{query}': {str(e)}")
        return {"content": "Search failed", "citations": []}

def generate_report(topic, research_data, length="medium"):
    """Generate a structured report from research with specified length"""
    logger.info(f"Generating {length} report for topic: {topic}")
    
    # Check if client is initialized
    if not client:
        logger.error("Groq client not initialized: GROQ_API_KEY not configured")
        return "Error: GROQ_API_KEY not configured. Please set your API key."
    
    # Define length parameters
    length_params = {
        "short": ("brief", 300, "1-2 bullet points"),
        "medium": ("concise", 700, "3-5 bullet points"),
        "long": ("detailed", 1200, "5-8 bullet points")
    }
    
    length_type, max_tokens, bullet_points = length_params.get(length, length_params["medium"])
    
    prompt = f"""Based on this research about "{topic}":

{research_data}

Create a {length_type} report with:
1. Overview (2-3 sentences)
2. Key Points ({bullet_points})
3. Conclusion (1-2 sentences)

Keep it professional and informative."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        
        report = response.choices[0].message.content
        logger.info(f"Report generated successfully for '{topic}' ({length} length)")
        return report
    except Exception as e:
        logger.error(f"Error generating report for '{topic}': {str(e)}")
        return f"Error generating report: {str(e)}. Please try again."

def save_report(topic, report, citations=None):
    """Save report to file with timestamp and citations"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{topic.replace(' ', '_')}_{timestamp}.txt"
    
    try:
        with open(filename, "w") as f:
            f.write(f"Research Report: {topic}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(report)
            
            # Add citations section
            if citations:
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("CITATIONS\n")
                f.write("=" * 60 + "\n")
                for citation in citations:
                    f.write(f"{citation}\n")
        
        logger.info(f"Report saved successfully: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving report for topic '{topic}': {str(e)}")
        return None

def research_agent(topic, queries=None, length="medium"):
    """Main research flow with multiple queries - with console output"""
    
    print(f"\n🔍 Researching: {topic}")
    print("-" * 60)
    print(f"⏳ Searching {len(queries) + 1 if queries else 1} query/queries for information...")
    
    result = research_agent_core(topic, queries, length)
    
    if result["filename"]:
        print("✓ Information gathered")
        print(f"⏳ Generating {length} report...")
        print("✓ Report generated")
        print("⏳ Saving report...")
        print(f"✓ Report saved as: {result['filename']}")
    
    return result


def research_agent_core(topic, queries=None, length="medium"):
    """Main research flow with multiple queries - core function without console output (for web app)"""
    logger.info(f"Starting research for topic: {topic} (length: {length})")
    
    try:
        # If no additional queries provided, use the main topic
        if not queries:
            queries = [topic]
        else:
            queries = [topic] + queries
        
        logger.info(f"Total queries to search: {len(queries)}")
        
        # Step 1: Multi-search
        all_research_data = []
        all_citations = []
        successful_searches = 0
        
        for i, query in enumerate(queries, 1):
            logger.debug(f"Executing search {i}/{len(queries)}: {query}")
            search_result = search_topic(query)
            # Only add non-empty results
            if search_result['content'] and "No information found" not in search_result['content'] and "Search failed" not in search_result['content']:
                all_research_data.append(f"\n--- Search: {query} ---\n{search_result['content']}")
                successful_searches += 1
            all_citations.extend(search_result['citations'])
        
        logger.info(f"Completed searches: {successful_searches}/{len(queries)} successful")
        
        # Check if we got any successful searches
        if successful_searches == 0:
            logger.warning(f"No successful searches for topic '{topic}' - using LLM fallback")
            # Use LLM to generate content when no search results available
            if client:
                fallback_prompt = f"""Generate a comprehensive report about "{topic}". 
Include:
1. Overview (2-3 sentences)
2. Key Points (3-5 bullet points)
3. Conclusion (1-2 sentences)

Make it informative and well-structured."""
                try:
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": fallback_prompt}],
                        max_tokens=700
                    )
                    report = response.choices[0].message.content
                    logger.info(f"Generated report using LLM fallback for '{topic}'")
                    filename = save_report(topic, report, [])
                    return {"report": report, "filename": filename, "citations": []}
                except Exception as e:
                    logger.error(f"LLM fallback failed: {str(e)}")
                    return {"report": f"❌ Could not find information. Error: {str(e)}", "filename": None, "citations": []}
            else:
                return {"report": "❌ Could not find enough information. Try different topics.", "filename": None, "citations": []}
        
        combined_research = "\n".join(all_research_data)
        
        # Step 2: Generate report
        report = generate_report(topic, combined_research, length)
        
        # Step 3: Save
        filename = save_report(topic, report, all_citations)
        
        logger.info(f"Research completed successfully for '{topic}' - saved as {filename}")
        return {"report": report, "filename": filename, "citations": all_citations}
    except Exception as e:
        logger.error(f"Error in research_agent_core for topic '{topic}': {str(e)}", exc_info=True)
        return {"report": f"Error during research: {str(e)}", "filename": None, "citations": []}

# Main interface
if __name__ == "__main__":
    print("=" * 60)
    print("RESEARCH ASSISTANT")
    print("=" * 60)
    print("I'll research any topic and create a report for you.")
    print("Features: Multiple queries, citations, and customizable length")
    print("Type 'quit' to exit")
    print("=" * 60)

    while True:
        topic = input("\n📝 Enter main research topic: ").strip()
        
        if topic.lower() == 'quit':
            print("\n👋 Goodbye!")
            break
        
        if not topic:
            continue
        
        # Ask for additional search queries
        additional_queries = input("📌 Enter additional search queries (comma-separated, or press Enter to skip): ").strip()
        queries = [q.strip() for q in additional_queries.split(",")] if additional_queries else None
        
        # Ask for report length
        print("\n📄 Report length options: short | medium (default) | long")
        length = input("Select report length: ").strip().lower()
        if length not in ["short", "medium", "long"]:
            length = "medium"
        
        # Run research
        print(f"\n🔍 Researching: {topic}")
        print("-" * 60)
        print(f"⏳ Searching {len(queries) if queries else 1} query/queries for information...")
        result = research_agent(topic, queries, length)
        
        if result["filename"]:
            print("✓ Information gathered")
            print(f"⏳ Generating {length} report...")
            print("✓ Report generated")
            print("⏳ Saving report...")
            print(f"✓ Report saved as: {result['filename']}")
            
            # Display report
            print("\n" + "=" * 60)
            print("REPORT")
            print("=" * 60)
            print(result["report"])
            print("=" * 60)
            
            # Display citations if available
            if result["citations"]:
                print("\n📚 CITATIONS:")
                for citation in result["citations"]:
                    print(f"  • {citation}")
        else:
            print(result["report"])
        
        # Ask if they want another
        another = input("\nResearch another topic? (yes/no): ").strip().lower()
        if another != 'yes':
            print("\n👋 Goodbye!")
            break