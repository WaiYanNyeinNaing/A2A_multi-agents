# tools/interactive_interface.py
"""
Interactive A2A Agent Interface
- Enter custom prompts for any agent
- Save generated results automatically
- Simple command-line interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import base64
from datetime import datetime
from pathlib import Path
from core import A2AClient

# Create results directory
RESULTS_DIR = Path("my_results")
RESULTS_DIR.mkdir(exist_ok=True)

def save_result(content, content_type, agent_name, custom_name=None):
    """Save generated content to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if custom_name:
        # Clean custom name for filename
        clean_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')[:30]  # Limit length
    else:
        clean_name = "result"
    
    if content_type == "text":
        filename = f"{agent_name}_{clean_name}_{timestamp}.txt"
        filepath = RESULTS_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"💾 Saved text: {filepath}")
        return str(filepath)
    
    elif content_type == "image":
        filename = f"{agent_name}_{clean_name}_{timestamp}.png"
        filepath = RESULTS_DIR / filename
        # content is base64 encoded
        image_bytes = base64.b64decode(content)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        print(f"💾 Saved image: {filepath}")
        return str(filepath)
    
    elif content_type == "json":
        filename = f"{agent_name}_{clean_name}_{timestamp}.json"
        filepath = RESULTS_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved JSON: {filepath}")
        return str(filepath)
    
    return None

def display_and_save_result(result, agent_name, custom_name=None):
    """Display result and save to file - Enhanced with multi-artifact support"""
    saved_files = []
    
    if not result["success"]:
        print(f"❌ {agent_name} failed: {result.get('error')}")
        return saved_files
    
    client = A2AClient()
    extracted = client.extract_result(result["task_data"])
    
    print(f"✅ {agent_name} completed successfully!")
    print(f"📋 Primary result type: {extracted['type']}")
    
    # Handle primary extracted result
    if extracted["type"] == "text":
        content = extracted["data"]
        print(f"\n📝 Generated Text ({len(content)} characters):")
        print("=" * 60)
        print(content)  # Show full content, no truncation
        print("=" * 60)
        
        text_name = custom_name if custom_name else "text_result"
        filepath = save_result(content, "text", agent_name, text_name)
        if filepath:
            saved_files.append(filepath)
    
    elif extracted["type"] == "file":
        file_data = extracted["data"]
        if file_data.get("mimeType") == "image/png" and file_data.get("bytes"):
            print(f"\n🎨 Generated Image: {file_data.get('name', 'Unnamed')}")
            print(f"   Image size: {len(base64.b64decode(file_data['bytes']))} bytes")
            
            image_name = custom_name if custom_name else "image_result"
            filepath = save_result(file_data["bytes"], "image", agent_name, image_name)
            if filepath:
                saved_files.append(filepath)
        else:
            print(f"\n📄 File result: {file_data}")
    
    elif extracted["type"] == "data":
        data = extracted["data"]
        print(f"\n📊 Structured Data:")
        print("=" * 60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("=" * 60)
        
        data_name = custom_name if custom_name else "data_result"
        filepath = save_result(data, "json", agent_name, data_name)
        if filepath:
            saved_files.append(filepath)
    
    # Process all artifacts for additional content
    if "task_data" in result:
        task_data = result["task_data"]
        artifacts = task_data.get("artifacts", [])
        
        if len(artifacts) > 0:
            print(f"\n🔍 Processing {len(artifacts)} artifact(s) for additional content...")
            
            for i, artifact in enumerate(artifacts):
                parts = artifact.get("parts", [])
                
                for j, part in enumerate(parts):
                    part_type = part.get("type", "unknown")
                    
                    # Handle file parts (images)
                    if part_type == "file" and part.get("file", {}).get("bytes"):
                        file_info = part["file"]
                        if file_info.get("mimeType") == "image/png":
                            print(f"   🎨 Found additional image: {file_info.get('name', 'unnamed.png')}")
                            image_bytes = file_info["bytes"]
                            image_size = len(base64.b64decode(image_bytes))
                            print(f"   📏 Size: {image_size} bytes")
                            
                            # Save the image with descriptive name
                            if custom_name:
                                image_name = f"{custom_name}_image_{i}_{j}"
                            else:
                                image_name = f"artifact_{i}_image_{j}"
                            
                            filepath = save_result(image_bytes, "image", agent_name, image_name)
                            if filepath:
                                saved_files.append(filepath)
                                print(f"   💾 Saved: {filepath}")
                    
                    # Handle substantial text parts
                    elif part_type == "text":
                        text_content = part.get("text", "")
                        if text_content and len(text_content) > 200:  # Only save substantial text
                            print(f"   📝 Found additional text content ({len(text_content)} characters)")
                            print("   " + "=" * 50)
                            print(f"   {text_content}")  # Show full text content
                            print("   " + "=" * 50)
                            
                            if custom_name:
                                text_name = f"{custom_name}_text_{i}_{j}"
                            else:
                                text_name = f"artifact_{i}_text_{j}"
                            
                            filepath = save_result(text_content, "text", agent_name, text_name)
                            if filepath:
                                saved_files.append(filepath)
                                print(f"   💾 Saved: {filepath}")
                    
                    # Handle data parts with substantial content
                    elif part_type == "data":
                        data_content = part.get("data", {})
                        if data_content and isinstance(data_content, dict) and len(data_content) > 1:
                            print(f"   📊 Found additional structured data")
                            
                            if custom_name:
                                data_name = f"{custom_name}_data_{i}_{j}"
                            else:
                                data_name = f"artifact_{i}_data_{j}"
                            
                            filepath = save_result(data_content, "json", agent_name, data_name)
                            if filepath:
                                saved_files.append(filepath)
                                print(f"   💾 Saved: {filepath}")
    
    # Save complete task data for debugging
    if custom_name:
        complete_name = f"{custom_name}_complete"
    else:
        complete_name = "complete_response"
    
    complete_filepath = save_result(result["task_data"], "json", agent_name, complete_name)
    if complete_filepath:
        saved_files.append(complete_filepath)
    
    return saved_files

def show_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("🤖 A2A AGENT INTERACTIVE INTERFACE")
    print("="*60)
    print("1. 🎯 Assistant Agent (Orchestrator) - Coordinates multiple agents")
    print("2. ✍️  Writing Specialist - Creates articles and content")
    print("3. 🎨 Image Generation Specialist - Creates images")
    print("4. 🔍 Research Specialist - Web search and data collection")
    print("5. 📊 Report Writing Specialist - Creates comprehensive reports")
    print("6. 📋 Check Agent Status")
    print("7. 📂 View Saved Results")
    print("8. ❌ Exit")
    print("="*60)

def show_examples(agent_type):
    """Show example prompts for each agent"""
    examples = {
        "assistant": [
            "Create an article about space exploration and generate a rocket image", 
            "Write about climate change and create environmental visuals",
            "Help me with content about artificial intelligence - text and images",
            "Research renewable energy and create a comprehensive report with visuals"
        ],
        "writing": [
            "Write a comprehensive article about quantum computing",
            "Create a professional blog post about sustainable technology", 
            "Write an informative piece about the future of transportation",
            "Compose an article about the benefits of renewable energy"
        ],
        "image": [
            "Generate a beautiful mountain landscape at sunrise",
            "Create a futuristic cityscape with flying cars",
            "Generate a professional office workspace environment",
            "Create an image of a sustainable energy facility"
        ],
        "research": [
            "Research the latest developments in artificial intelligence",
            "Find information about climate change impacts in 2024",
            "Search for recent studies on renewable energy efficiency",
            "Fact-check: Electric vehicles produce zero emissions"
        ],
        "report": [
            "Create a comprehensive report on AI trends (provide research data as input)",
            "Generate an executive summary from research findings",
            "Convert this research into an HTML report",
            "Create a slide presentation outline from research data"
        ]
    }
    
    if agent_type in examples:
        print(f"\n💡 Example prompts for {agent_type}:")
        for i, example in enumerate(examples[agent_type], 1):
            print(f"   {i}. {example}")
        print()

async def check_agent_status():
    """Check status of all agents"""
    print("\n🔍 Checking Agent Status...")
    print("-" * 40)
    
    agents = {
        "Assistant Agent": "http://127.0.0.1:8000",
        "Writing Specialist": "http://127.0.0.1:8002", 
        "Image Generation Specialist": "http://127.0.0.1:8001",
        "Research Specialist": "http://127.0.0.1:8003",
        "Report Writing Specialist": "http://127.0.0.1:8004"
    }
    
    client = A2AClient()
    
    for name, url in agents.items():
        try:
            card = await client.discover_agent(url)
            print(f"✅ {name}: Online - {card['name']}")
        except Exception as e:
            print(f"❌ {name}: Offline - {str(e)[:50]}...")

def view_saved_results():
    """Show list of saved results"""
    print(f"\n📂 Saved Results in {RESULTS_DIR}:")
    print("-" * 40)
    
    files = list(RESULTS_DIR.glob("*"))
    if not files:
        print("   No saved results found.")
        return
    
    # Group files by type
    text_files = [f for f in files if f.suffix == '.txt']
    image_files = [f for f in files if f.suffix == '.png'] 
    json_files = [f for f in files if f.suffix == '.json']
    
    if text_files:
        print(f"📝 Text Files ({len(text_files)}):")
        for f in sorted(text_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            print(f"   • {f.name}")
    
    if image_files:
        print(f"🎨 Image Files ({len(image_files)}):")
        for f in sorted(image_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            print(f"   • {f.name}")
    
    if json_files:
        print(f"📊 JSON Files ({len(json_files)}):")
        for f in sorted(json_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            print(f"   • {f.name}")
    
    total_files = len(files)
    if total_files > 15:
        print(f"   ... and {total_files - 15} more files")

async def handle_agent_request(agent_name, agent_url, agent_type):
    """Handle request to specific agent"""
    print(f"\n🎯 Selected: {agent_name}")
    
    # Show examples
    show_examples(agent_type)
    
    # Get user input
    print("✏️ Enter your prompt:")
    user_prompt = input("👤 Your request: ").strip()
    
    if not user_prompt:
        print("❌ Empty prompt. Returning to menu.")
        return
    
    # Optional custom name for saving
    print("\n💾 Optional: Give this request a custom name for saving (or press Enter to skip):")
    custom_name = input("📝 Custom name: ").strip()
    
    # Execute request
    print(f"\n🚀 Sending request to {agent_name}...")
    print(f"📝 Prompt: {user_prompt}")
    
    try:
        client = A2AClient()
        
        # Show progress
        print("⏳ Processing... (this may take a moment)")
        
        result = await client.send_and_wait(agent_url, user_prompt, max_wait=90)
        
        # Display and save results
        saved_files = display_and_save_result(result, agent_name.replace(" ", "_"), custom_name)
        
        if saved_files:
            print(f"\n✅ Results saved to {len(saved_files)} file(s)")
        
        print("\n🎉 Request completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Main interactive loop"""
    print("🎉 Welcome to the A2A Agent Interactive Interface!")
    print("💡 This tool lets you send custom prompts to AI agents and save the results.")
    
    agents = {
        "1": ("Assistant Agent (Orchestrator)", "http://127.0.0.1:8000", "assistant"),
        "2": ("Writing Specialist", "http://127.0.0.1:8002", "writing"),
        "3": ("Image Generation Specialist", "http://127.0.0.1:8001", "image"),
        "4": ("Research Specialist", "http://127.0.0.1:8003", "research"),
        "5": ("Report Writing Specialist", "http://127.0.0.1:8004", "report")
    }
    
    while True:
        show_menu()
        
        choice = input("👤 Select an option (1-6): ").strip()
        
        if choice in agents:
            agent_name, agent_url, agent_type = agents[choice]
            await handle_agent_request(agent_name, agent_url, agent_type)
            
        elif choice == "6":
            await check_agent_status()
            
        elif choice == "7":
            view_saved_results()
            
        elif choice == "8":
            print("\n👋 Thank you for using the A2A Agent Interface!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-8.")
        
        # Pause before showing menu again
        input("\n⏳ Press Enter to continue...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")