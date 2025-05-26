import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, set_default_openai_client, set_tracing_disabled
from agents.model_settings import ModelSettings
from pydantic import BaseModel
from typing import Dict, List, Optional
import requests
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from openai import AsyncAzureOpenAI
import base64
from io import BytesIO
import re

# Page configuration
st.set_page_config(
    page_title="Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a cleaner look
st.markdown("""
<style>
    .main {
        padding: 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .report-container {
        margin-top: 2rem;
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .download-section {
        display: flex;
        gap: 10px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    .download-section > div {
        flex: 1;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session states
if 'report' not in st.session_state:
    st.session_state.report = None
if 'html_report' not in st.session_state:
    st.session_state.html_report = None
if 'searches_completed' not in st.session_state:
    st.session_state.searches_completed = 0
if 'total_searches' not in st.session_state:
    st.session_state.total_searches = 0
if 'research_complete' not in st.session_state:
    st.session_state.research_complete = False

# Load environment variables
load_dotenv()

# Configure OpenAI client
def initialize_openai():
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
    )
    set_default_openai_client(openai_client)
    
    # Disable tracing if needed
    set_tracing_disabled(True)

# ===== SERPER API SEARCH TOOL =====
@function_tool
def serper_web_search(query: str, num_results: Optional[int] = None) -> Dict[str, List[Dict]]:
    """
    Search the web using Serper API.
    
    Args:
        query: The search query
        num_results: Number of results to return
    """
    # Update the progress bar in the UI
    st.session_state.searches_completed += 1
    
    # Set default value
    if num_results is None:
        num_results = 15
    
    try:
        # Get API key
        api_key = os.environ.get("SERPER_API")
        if not api_key:
            st.error("ERROR: SERPER_API environment variable is not set")
            return {"results": [], "error": "API key not set"}
        
        # Set up headers
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        # Set up payload
        payload = {
            "q": query,
            "num": num_results
        }
        
        # Make the request
        response = requests.post(
            "https://google.serper.dev/search", 
            headers=headers, 
            json=payload
        )
        
        # Check response status
        if response.status_code == 200:
            data = response.json()
            
            # Extract results
            results = []
            if 'organic' in data:
                for item in data['organic'][:num_results]:
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })
                    
                # If there are knowledge graph results, add them too
                if 'knowledgeGraph' in data:
                    kg = data['knowledgeGraph']
                    if 'title' in kg and 'attributes' in kg:
                        results.append({
                            'title': f"Knowledge: {kg.get('title', '')}",
                            'link': kg.get('website', ''),
                            'snippet': str(kg.get('attributes', {}))
                        })
                
                # Add local results if available (for location-based searches)
                if 'local' in data and len(data['local']) > 0:
                    for item in data['local'][:num_results]:
                        results.append({
                            'title': f"Local: {item.get('title', '')}",
                            'link': item.get('website', '') or item.get('linkUrl', ''),
                            'snippet': f"Address: {item.get('address', '')}, Phone: {item.get('phone', '')}"
                        })
                
                return {"results": results}
            else:
                return {"results": []}
        else:
            return {"results": [], "error": f"Status code: {response.status_code}"}
        
    except Exception as e:
        import traceback
        st.error(f"Error with Serper API: {str(e)}")
        return {"results": [], "error": str(e)}

# ===== SEARCH AGENT =====
def create_search_agent(num_results):
    search_instructions = """You are a research assistant. Given a search term, you search the web for that term and 
    produce a concise summary of the results. The summary must be 2-3 paragraphs and less than 300 
    words. Capture the main points. Write succinctly, no need to have complete sentences or good 
    grammar. This will be consumed by someone synthesizing a report, so it's vital you capture the 
    essence and ignore any fluff. Do not include any additional commentary other than the summary itself.
    
    IMPORTANT: When you find useful resources, please include their full URLs in your summary.
    Format them as: "Resource: [resource name](url)" at the end of your summary for each important resource.
    This will allow direct linking to the resources in the final report."""

    search_agent = Agent(
        name="Search agent",
        instructions=search_instructions,
        tools=[serper_web_search],
        model="gpt-4.1-t93a-temp",
        model_settings=ModelSettings(tool_choice="required"),
    )
    return search_agent

# ===== STRUCTURED OUTPUT MODELS =====
class WebSearchItem(BaseModel):
    reason: str
    query: str

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]

class ReportData(BaseModel):
    short_summary: str
    markdown_report: str
    follow_up_questions: list[str]

class HTMLReportData(BaseModel):
    html_content: str
    report_title: str

# ===== PLANNER AGENT =====
def create_planner_agent(how_many_searches):
    planner_instructions = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
    to perform to best answer the query. Output {how_many_searches} terms to query for."

    planner_agent = Agent(
        name="PlannerAgent",
        instructions=planner_instructions,
        model="gpt-4.1-t93a-temp",
        output_type=WebSearchPlan,
    )
    return planner_agent

# ===== EMAIL ENHANCEMENT AGENTS =====
def create_email_agents(recipient_email):
    # Subject Writer Agent
    subject_instructions = """You can write a subject for a cold sales email.
    You are given a message and you need to write a subject for an email that is likely to get a response.
    The subject should be catchy, concise, and relevant to the content of the email.
    Subjects should be between 5-9 words and should pique curiosity.
    """

    subject_writer = Agent(
        name="Email subject writer", 
        instructions=subject_instructions, 
        model="gpt-4.1-t93a-temp"
    )
    subject_tool = subject_writer.as_tool(
        tool_name="subject_writer", 
        tool_description="Write a subject for a cold sales email"
    )

    # HTML Converter Agent
    html_instructions = """You can convert a text email body to an HTML email body.
    You are given a text email body which might have some markdown
    and you need to convert it to an HTML email body with simple, clear, compelling layout and design.
    Use professional styling with:
    - Clean, readable typography
    - Appropriate spacing and margins
    - Responsive design principles
    - Highlight key points with formatting (bold, italic, etc.)
    - Add visual hierarchy with headings and sections
    - Include a clean signature area at the bottom
    - Use a color scheme that conveys professionalism (subtle blues, grays)
    - Ensure the design works well on mobile devices

    Make sure to convert all markdown to proper HTML formatting.
    """

    html_converter = Agent(
        name="HTML email body converter", 
        instructions=html_instructions, 
        model="gpt-4.1-t93a-temp"
    )
    html_tool = html_converter.as_tool(
        tool_name="html_converter",
        tool_description="Convert a text email body to an HTML email body"
    )

    # Enhanced Email Agent
    email_instructions = """You are able to send a nicely formatted HTML email based on a detailed report.
    You will be provided with a detailed report. You should first use the subject_writer tool to create
    a compelling subject line. Then use the html_converter tool to transform the report into a beautiful,
    professional HTML email. Finally, use the send_html_email tool to send the email.

    Follow these steps exactly:
    1. Use subject_writer to generate an effective subject line
    2. Use html_converter to convert the report content to professional HTML
    3. Use send_html_email to send the final email

    Make sure the email looks professional and follows best practices for business communication.
    """

    @function_tool
    def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
        """ Send out an email with the given subject and HTML body to all sales prospects """
        try:
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
            from_email = Email("jackbutnot77@gmail.com")  # Change to your verified sender
            to_email = To(recipient_email)  # Use the recipient email from the form
            content = Content("text/html", html_body)
            mail = Mail(from_email, to_email, subject, content).get()
            response = sg.client.mail.send.post(request_body=mail)
            return {"status": "success" if response.status_code < 300 else "failed"}
        except Exception as e:
            st.error(f"Email sending error: {str(e)}")
            return {"status": "failed", "error": str(e)}

    email_agent = Agent(
        name="Enhanced Email agent",
        instructions=email_instructions,
        tools=[subject_tool, html_tool, send_html_email],
        model="gpt-4.1-t93a-temp",
    )
    
    return email_agent

# ===== WRITER AGENT =====
def create_writer_agent():
    writer_instructions = (
        "You are a senior researcher tasked with writing a cohesive report for a research query. "
        "You will be provided with the original query, and some initial research done by a research assistant.\n"
        "You should first come up with an outline for the report that describes the structure and "
        "flow of the report. Then, generate the report and return that as your final output.\n"
        "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
        "for 5-10 pages of content, at least 1000 words.\n"
        "IMPORTANT: When including URLs or links to resources in your report, make sure they are formatted "
        "as clickable markdown links: [Resource Name](https://url.com). Include all relevant resource links "
        "from the search results. If the search results contain resource links, extract them "
        "and include them in your report as properly formatted markdown links."
    )

    writer_agent = Agent(
        name="WriterAgent",
        instructions=writer_instructions,
        model="gpt-4.1-t93a-temp",
        output_type=ReportData,
    )
    return writer_agent

# ===== HTML REPORT AGENT =====
def create_html_report_agent():
    html_report_instructions = """You are a professional HTML report generator. Your task is to convert a 
    markdown research report into a beautiful, well-formatted HTML document that can be displayed in a browser
    or downloaded as PDF.
    
    Your HTML report should include:
    1. A clean, professional design with proper styling
    2. Responsive layout that works well on both desktop and mobile
    3. A table of contents with links to sections
    4. Well-formatted headings, paragraphs, lists, and other elements
    5. Properly formatted hyperlinks (all URLs should be clickable)
    6. A print-friendly design that will look good when converted to PDF
    7. Modern, professional styling with appropriate use of color, typography, and white space
    8. Footer with the date the report was generated
    
    The HTML should include a complete <head> section with appropriate metadata, CSS styling, 
    and everything needed for a standalone HTML document. All CSS should be included within the HTML
    (no external stylesheet references).
    
    Make sure all links from the original markdown are properly formatted as HTML links. 
    The report should have a professional appearance suitable for business settings.
    """

    html_report_agent = Agent(
        name="HTMLReportAgent",
        instructions=html_report_instructions,
        model="gpt-4.1-t93a-temp",
        output_type=HTMLReportData,
    )
    return html_report_agent

# ===== RESEARCH FLOW FUNCTIONS =====
async def plan_searches(query: str, how_many_searches: int):
    """ Use the planner_agent to plan which searches to run for the query """
    planner_agent = create_planner_agent(how_many_searches)
    result = await Runner.run(planner_agent, f"Query: {query}")
    st.session_state.total_searches = len(result.final_output.searches)
    return result.final_output

async def search(item: WebSearchItem, num_results: int):
    """ Use the search agent to run a web search for each item in the search plan """
    search_agent = create_search_agent(num_results)
    input = f"Search term: {item.query}\nReason for searching: {item.reason}"
    result = await Runner.run(search_agent, input)
    
    # Update the progress text in the UI
    status_placeholder = st.session_state.get('status_placeholder')
    if status_placeholder:
        status_placeholder.text(f"Searching ({st.session_state.searches_completed}/{st.session_state.total_searches}): {item.query}")
    
    return result.final_output

async def perform_searches(search_plan: WebSearchPlan, num_results: int):
    """ Call search() for each item in the search plan """
    tasks = [asyncio.create_task(search(item, num_results)) for item in search_plan.searches]
    results = await asyncio.gather(*tasks)
    return results

async def write_report(query: str, search_results: list[str]):
    """ Use the writer agent to write a report based on the search results"""
    writer_agent = create_writer_agent()
    input = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input)
    return result.final_output

async def create_html_report(report_data: ReportData, query: str):
    """ Use the HTML report agent to create an HTML version of the report """
    html_report_agent = create_html_report_agent()
    input = (
        f"Original query: {query}\n\n"
        f"Report summary: {report_data.short_summary}\n\n"
        f"Report content:\n{report_data.markdown_report}"
    )
    result = await Runner.run(html_report_agent, input)
    return result.final_output

async def send_enhanced_email(report: ReportData, query: str, recipient_email: str):
    """ Use the enhanced email agent to create and send a professional HTML email """
    email_agent = create_email_agents(recipient_email)
    # Provide both the report and the original query
    input_text = f"Original Query: {query}\n\nReport Content:\n\n{report.markdown_report}"
    result = await Runner.run(email_agent, input_text)
    return result.final_output

# ===== MAIN RESEARCH FUNCTION =====
async def run_deep_research(query: str, num_results: int, how_many_searches: int, recipient_email: str):
    # Reset progress tracking
    st.session_state.searches_completed = 0
    st.session_state.research_complete = False
    
    # Initialize OpenAI
    initialize_openai()
    
    # Create progress placeholder
    progress_bar = st.progress(0)
    status_text = st.empty()
    st.session_state.status_placeholder = status_text
    
    try:
        # Planning phase
        status_text.text("Planning searches...")
        search_plan = await plan_searches(query, how_many_searches)
        progress_bar.progress(10)
        
        # Search phase
        status_text.text(f"Performing searches (0/{st.session_state.total_searches})...")
        search_results = await perform_searches(search_plan, num_results)
        progress_bar.progress(50)
        
        # Report writing phase
        status_text.text("Writing comprehensive report...")
        report = await write_report(query, search_results)
        progress_bar.progress(70)
        
        # Create HTML report
        status_text.text("Creating HTML version of the report...")
        html_report = await create_html_report(report, query)
        progress_bar.progress(85)
        
        # Email sending phase
        status_text.text("Sending email report...")
        await send_enhanced_email(report, query, recipient_email)
        
        # Complete
        progress_bar.progress(100)
        status_text.text("Research completed!")
        st.session_state.research_complete = True
        st.session_state.report = report
        st.session_state.html_report = html_report
        
        return report, html_report
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None, None

# ===== PDF GENERATION HELPERS =====
def get_pdf_download_link(html_content, filename="research_report.pdf"):
    """Generate a link to download the HTML as PDF"""
    # This function would typically use a PDF generation library
    # For simplicity, we're just providing the HTML download with instructions
    # In a production environment, you would use a library like WeasyPrint or wkhtmltopdf
    
    html_b64 = base64.b64encode(html_content.encode()).decode()
    href = f'data:text/html;base64,{html_b64}'
    return href

# Function to extract and format resources from the report
def extract_resources(markdown_content):
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_content)
    if not links:
        # Try to find URLs directly
        urls = re.findall(r'https?://[^\s\)]+', markdown_content)
        if urls:
            return [(url, url) for url in urls]
    return links

# ===== STREAMLIT UI =====
def main():
    st.title("🔍 Research Agent")
    st.subheader("Your AI-powered research assistant")
    
    with st.form("research_form"):
        st.write("Enter your research query and preferences below:")
        
        query = st.text_area("Research Query", 
                           placeholder="E.g., Halal food near Chicago, IL, 60090, maximum distance drive 45min")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_results = st.slider("Number of search results per search", 
                                  min_value=5, max_value=30, value=15, step=5)
        
        with col2:
            how_many_searches = st.slider("Number of searches to perform", 
                                        min_value=3, max_value=15, value=7, step=1)
                
        recipient_email = st.text_input("Email Address to receive the report", 
                                      placeholder="your.email@example.com")
        
        submit_button = st.form_submit_button("Start Research")
        
        if submit_button:
            if not query:
                st.error("Please enter a research query")
            elif not recipient_email or "@" not in recipient_email:
                st.error("Please enter a valid email address")
            else:
                with st.spinner("Starting research process..."):
                    asyncio.run(run_deep_research(query, num_results, how_many_searches, recipient_email))
    
    # Display results after form submission
    if st.session_state.research_complete and st.session_state.report:
        report = st.session_state.report
        html_report = st.session_state.html_report
        
        st.success(f"✅ Research completed and report sent to {recipient_email}")
        
        with st.expander("Report Summary", expanded=True):
            st.write(report.short_summary)
        
        # Download buttons section
        st.subheader("Download Options")
        col1, col2 = st.columns(2)
        
        with col1:
            # Markdown download
            st.download_button(
                label="📄 Download as Markdown",
                data=report.markdown_report,
                file_name="research_report.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col2:
            # HTML/PDF download
            if html_report:
                html_content = html_report.html_content
                html_download_link = get_pdf_download_link(html_content)
                
                st.download_button(
                    label="📑 Download as HTML/PDF",
                    data=html_content,
                    file_name="research_report.html",
                    mime="text/html",
                    use_container_width=True
                )
                
                # Instructions for PDF conversion
                with st.expander("How to convert HTML to PDF"):
                    st.write("""
                    1. Download the HTML file
                    2. Open it in your web browser
                    3. Use the browser's print function (Ctrl+P or Cmd+P)
                    4. Select "Save as PDF" as the destination
                    5. Click "Save" to generate your PDF
                    """)
        
        # Full report section
        with st.expander("Full Research Report", expanded=False):
            # Use unsafe_allow_html=True to ensure links are clickable
            st.markdown(report.markdown_report, unsafe_allow_html=True)
        
        # If HTML report is available, provide a preview option
        if html_report:
            with st.expander("HTML Report Preview", expanded=False):
                st.components.v1.html(html_report.html_content, height=600, scrolling=True)
        
        # Extract and display links from the report
        with st.expander("Resource Links", expanded=True):
            st.write("Here are the links to resources found during research:")
            
            # Extract links from the report
            links = extract_resources(report.markdown_report)
            
            if links:
                for i, (text, url) in enumerate(links):
                    st.markdown(f"{i+1}. [{text}]({url})", unsafe_allow_html=True)
            else:
                st.write("No resource links were found in the report.")
            
        with st.expander("Follow-up Questions", expanded=False):
            for i, question in enumerate(report.follow_up_questions):
                st.write(f"{i+1}. {question}")

if __name__ == "__main__":
    main()