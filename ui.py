
import requests
import os
from pathlib import Path


st.set_page_config(
    page_title="AI-Bookshelf RAG",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoint
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000")

# Custom styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 AI-Bookshelf RAG")
st.markdown("*Retrieval-Augmented Generation for your personal library*")

# Create tabs
tab1, tab2, tab3 = st.tabs(["🔍 Search", "📖 Books", "⬆️ Upload"])

# ==================== TAB 1: SEARCH ====================
with tab1:
    st.header("Search Your Knowledge Base")
    
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
    
    # Query input
    user_input = st.chat_input("Ask a question about your books...")
    
    if user_input:
        # Store and display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get response from API
        try:
            with st.spinner("🔄 Searching and generating response..."):
                response = requests.post(
                    f"{API_BASE_URL}/query",
                    json={"query": user_input},
                    timeout=30
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    bot_response = response_data.get("answer", "No response generated.")
                    file_names = response_data.get("file_names", [])
                    num_results = response_data.get("num_results", 0)
                    
                    # Display response
                    with st.chat_message("assistant"):
                        st.markdown(bot_response)
                        
                        # Show sources
                        if file_names:
                            with st.expander("📄 Sources"):
                                for file_name in file_names:
                                    st.markdown(f"- {file_name}")
                    
                    # Store response
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                else:
                    st.error(f"API Error: {response.status_code}")
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ==================== TAB 2: BOOKS ====================
with tab2:
    st.header("📖 Available Books")
    
    try:
        with st.spinner("Loading books..."):
            response = requests.get(f"{API_BASE_URL}/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                embedded_files = data.get("embedded_files", [])
                total_files = data.get("total_files", 0)
                
                # Display statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📚 Total Books", total_files)
                with col2:
                    st.metric("✅ Status", "Running")
                with col3:
                    st.metric("🔄 Last Updated", "Now")
                
                # Display books list
                if embedded_files:
                    st.subheader(f"Embedded Books ({len(embedded_files)})")
                    
                    # Create a nice display for books
                    for idx, file_name in enumerate(embedded_files, 1):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"**{idx}. {file_name}**")
                        with col2:
                            st.write("✓ Embedded")
                else:
                    st.info("📭 No books embedded yet. Upload a PDF to get started!")
            else:
                st.error("Could not fetch book list from API")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the backend is running.")
    except Exception as e:
        st.error(f"❌ Error fetching books: {str(e)}")

# ==================== TAB 3: UPLOAD ====================
with tab3:
    st.header("⬆️ Upload New Book")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Select a PDF file to add to your knowledge base"
        )
    
    with col2:
        st.write("")  # Spacing
    
    if uploaded_file:
        st.markdown(f"**Selected file:** {uploaded_file.name}")
        st.markdown(f"**File size:** {uploaded_file.size / 1024:.2f} KB")
        
        if st.button("📤 Upload and Process", key="upload_btn", type="primary"):
            try:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    # Save uploaded file temporarily
                    pdf_path = f"pdf_references/{uploaded_file.name}"
                    os.makedirs("pdf_references", exist_ok=True)
                    
                    # Write file
                    with open(pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Send to API
                    response = requests.post(
                        f"{API_BASE_URL}/add-pdf",
                        json={"pdf_path": pdf_path},
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            st.success(f"✅ {uploaded_file.name} uploaded and processed successfully!")
                            st.balloons()
                        else:
                            st.error(f"❌ {result.get('message', 'Failed to process PDF')}")
                    else:
                        st.error(f"API Error: {response.status_code}")
            
            except Exception as e:
                st.error(f"❌ Error uploading file: {str(e)}")
    else:
        st.info("👆 Select a PDF file above to upload")
    
    # Info section
    with st.expander("ℹ️ Upload Information"):
        st.markdown("""
        - **Supported Format:** PDF only
        - **Processing:** Automatic chunking and embedding
        - **Storage:** Files saved to knowledge base
        - **Search:** Available immediately after upload
        """)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("---")
    st.subheader("⚙️ Settings")
    
    # API connection status
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.warning("⚠️ Backend Error")
    except:
        st.error("❌ Backend Offline")
    
    # Display API endpoint
    st.markdown(f"**API:** {API_BASE_URL}")
    
    st.markdown("---")
    st.markdown("""
    ### About AI-Bookshelf
    
    A Retrieval-Augmented Generation (RAG) system for:
    - 📚 Managing your personal book collection
    - 🔍 Intelligent search across documents
    - 💡 AI-powered responses with sources
    
    **Tech Stack:**
    - Milvus Vector DB
    - Sentence Transformers
    - OpenAI API
    - Flask Backend

    """)
    
    st.markdown("---")
    st.caption("AI-Bookshelf RAG v1.0 | November 2025")
