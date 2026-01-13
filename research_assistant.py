from groq import Groq
import requests
import json
from datetime import datetime

client = Groq(api_key="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")

def search_topic(query):
    """Search and return relevant info with citations"""
    url = f"https://api.duckduckgo.com/?q={query}&format=json"
    try:
        response = requests.get(url, timeout=5)
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
        return return_data
    except:
        return {"content": "Search failed", "citations": []}

def generate_report(topic, research_data, length="medium"):
    """Generate a structured report from research with specified length"""
    
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
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        return f"Error generating report: {str(e)}. Please try again."

def save_report(topic, report, citations=None):
    """Save report to file with timestamp and citations"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{topic.replace(' ', '_')}_{timestamp}.txt"
    
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
    
    return filename

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
    
    try:
        # If no additional queries provided, use the main topic
        if not queries:
            queries = [topic]
        else:
            queries = [topic] + queries
        
        # Step 1: Multi-search
        all_research_data = []
        all_citations = []
        successful_searches = 0
        
        for i, query in enumerate(queries, 1):
            search_result = search_topic(query)
            # Only add non-empty results
            if search_result['content'] and "No information found" not in search_result['content'] and "Search failed" not in search_result['content']:
                all_research_data.append(f"\n--- Search: {query} ---\n{search_result['content']}")
                successful_searches += 1
            all_citations.extend(search_result['citations'])
        
        # Check if we got any successful searches
        if successful_searches == 0:
            return {"report": "❌ Could not find enough information. Try different topics.", "filename": None, "citations": []}
        
        combined_research = "\n".join(all_research_data)
        
        # Step 2: Generate report
        report = generate_report(topic, combined_research, length)
        
        # Step 3: Save
        filename = save_report(topic, report, all_citations)
        
        return {"report": report, "filename": filename, "citations": all_citations}
    except Exception as e:
        print(f"Error in research_agent_core: {str(e)}")
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