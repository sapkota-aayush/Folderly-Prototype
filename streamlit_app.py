import streamlit as st
import time
from ai_integration import chat_with_ai_single, start_background_monitoring, stop_background_monitoring

# Page configuration
st.set_page_config(
    page_title="Folderly - Smart File Manager",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for beautiful animations and styling
st.markdown("""
<style>
    /* Beautiful gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    /* Main container styling */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Beautiful logo and header */
    .logo-container {
        text-align: center;
        margin-bottom: 3rem;
        position: relative;
    }
    
    .logo {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: logoFloat 4s ease-in-out infinite;
        display: block;
    }
    
    @keyframes logoFloat {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        25% { transform: translateY(-10px) rotate(2deg); }
        50% { transform: translateY(-5px) rotate(0deg); }
        75% { transform: translateY(-15px) rotate(-2deg); }
    }
    
    .logo-text {
        background: linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: bold;
        animation: gradientShift 3s ease infinite;
        margin-bottom: 0.5rem;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .tagline {
        color: #666;
        font-size: 1.1rem;
        font-style: italic;
        animation: fadeInUp 1s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Enhanced typing animation */
    .typing-container {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 15px;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        color: white;
        margin: 10px 0;
        animation: typingGlow 2s ease-in-out infinite;
    }
    
    @keyframes typingGlow {
        0%, 100% { box-shadow: 0 0 10px rgba(240, 147, 251, 0.5); }
        50% { box-shadow: 0 0 20px rgba(240, 147, 251, 0.8); }
    }
    
    .typing-dots {
        display: flex;
        gap: 3px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: white;
        animation: typingDot 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    .typing-dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes typingDot {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Beautiful chat messages */
    .chat-message {
        margin: 15px 0;
        padding: 20px;
        border-radius: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .chat-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    .chat-message:hover::before {
        transform: translateX(100%);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 15%;
        text-align: right;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .ai-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 15%;
        text-align: left;
        box-shadow: 0 5px 15px rgba(240, 147, 251, 0.3);
    }
    
    .chat-message:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    /* Enhanced input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 15px 25px;
        font-size: 16px;
        background: rgba(255, 255, 255, 0.9);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #764ba2;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.4);
        background: white;
    }
    
    /* Action buttons */
    .action-buttons {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 25px;
        font-weight: bold;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Welcome animation */
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        animation: welcomeBounce 2s ease-in-out;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes welcomeBounce {
        0% { transform: scale(0.8); opacity: 0; }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    /* Hide Streamlit elements */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize activity monitoring
if "monitoring_started" not in st.session_state:
    st.session_state.monitoring_started = False

# Main app
def main():
    # Start background monitoring if not already started
    if not st.session_state.monitoring_started:
        try:
            start_background_monitoring()
            st.session_state.monitoring_started = True
        except Exception as e:
            st.error(f"Could not start activity monitoring: {str(e)}")
    # Beautiful logo and header
    st.markdown("""
    <div class="logo-container">
        <div class="logo">🤖</div>
        <div class="logo-text">Folderly</div>
        <div class="tagline">Your Smart File Management Assistant</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message for new users
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-card">
            <h2>🎉 Welcome to Folderly!</h2>
            <p>Your intelligent file management companion. Ask me to list, create, move, or delete files on your desktop!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(f'<div class="chat-message {message["role"]}-message">{message["content"]}</div>', unsafe_allow_html=True)
        
        # User input
        if prompt := st.chat_input("What would you like to do with your files?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(f'<div class="chat-message user-message">{prompt}</div>', unsafe_allow_html=True)
            
            # Show enhanced typing indicator
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("""
                <div class="typing-container">
                    <span>🤖 AI is thinking</span>
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Get AI response
                response = chat_with_ai_single(prompt)
                
                # Enhanced typing animation with better timing
                full_response = response
                display_response = ""
                
                # Clear typing indicator
                message_placeholder.empty()
                
                # Type out response character by character
                for i, char in enumerate(full_response):
                    display_response += char
                    message_placeholder.markdown(f'<div class="chat-message ai-message">{display_response}</div>', unsafe_allow_html=True)
                    
                    # Vary typing speed for more natural feel
                    if char in ['.', '!', '?', '\n']:
                        time.sleep(0.1)  # Pause at punctuation
                    elif char == ' ':
                        time.sleep(0.01)  # Fast for spaces
                    else:
                        time.sleep(0.03)  # Normal speed
                
                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Quick action buttons
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("📁 List Files", key="list_files"):
                st.session_state.messages.append({"role": "user", "content": "list all my desktop files"})
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Files", key="delete_files"):
                st.session_state.messages.append({"role": "user", "content": "delete all txt files"})
                st.rerun()
        
        with col3:
            if st.button("📝 Create File", key="create_file"):
                st.session_state.messages.append({"role": "user", "content": "create a new file called test.txt"})
                st.rerun()
        
        with col4:
            if st.button("🔄 Undo", key="undo"):
                st.session_state.messages.append({"role": "user", "content": "undo it"})
                st.rerun()
        
        with col5:
            if st.button("📊 Activity", key="activity"):
                st.session_state.messages.append({"role": "user", "content": "show my recent activity"})
                st.rerun()

if __name__ == "__main__":
    main() 