
# Streamlit
import streamlit as st

# Mistral AI
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# General
import hmac

# -----------------------------------------------------------------------------

def ask_mistral(msgs):
    # Messages
    messages = [ ChatMessage(role="user", content=txt) for txt in msgs ]
    # No streaming
    model= "mistral-tiny"
    chat_response = client.chat(model=model, messages=messages,
                                max_tokens=None, temperature=0.7,
                                top_p=None, safe_prompt=False, random_seed=None)
    return chat_response

# Update
def update(*args):
    if args[0] in ("prompt", "ask", ):
        # Get and clear prompt
        txt = st.session_state.prompt
        st.session_state.prompt = ""
        # Process
        if not (txt is None or txt==''):
            # Clean
            txt = txt.strip()
            # Update messages
            st.session_state.messages.append(txt)
            # Ask Mistral AI
            chat_response = ask_mistral(st.session_state.messages)
            # Response
            r = [ c.message.content for c in chat_response.choices ]
            # Update history
            st.session_state.history.append(('R', '\n'.join(r)))
            st.session_state.history.append(('Q', txt))

def check_password():

    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")

    return False

# -----------------------------------------------------------------------------

# Very basic security check...
if not check_password():
    # Do not continue if check_password is not True
    st.stop()

# Mistral AI Client
client = MistralClient(api_key=st.secrets.api_key)

# Configuration
st.set_page_config(
    page_title="Mistral AI",
    page_icon=":gear:",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={}
)

# Session state
if not 'history' in st.session_state:
    st.session_state.history = []
if not 'messages' in st.session_state:
    st.session_state.messages = []
if not 'models' in st.session_state:
    list_models_response = client.list_models()
    models = [ d.id for d in list_models_response.data ]
    if 'mistral-tiny' in models:
        models.remove('mistral-tiny')
        models.insert(0, 'mistral-tiny')
    st.session_state.models = models

# Title
st.title(":gear: Mistral AI Chat")

# Prompt
### st.text_input("Ask for anything...", value=None, key="prompt", on_change=update, args=('prompt',), disabled=False)
st.text_input("Ask for anything...", value=None, placeholder="Talk to me...", key="prompt", disabled=False)

col1, col2 = st.columns([1, 1])
with col1:
    # Ask button
    st.button("Ask", type="primary", key="ask", on_click=update, args=("ask", ))
with col2:
    # Clear button
    if st.button("Restart", type="secondary"):
        st.session_state.history = []
        st.session_state.messages = []

# Discussion
for t, msg in st.session_state.history[::-1]:
    if t=='Q':
        st.write(f':blue[**{msg}**]')
    else:
        st.write(f'{msg}')

# Model parameters
st.divider()
st.write('**Mistral AI model parameters**')
col3, col4 = st.columns([1, 1])
with col3:
    # Models
    model = st.selectbox('Model', st.session_state.models, index=0, key='model')
with col4:
    # Temperature slider
    temperature = st.slider('Temperature', 0.0, 1.0, 0.7, 0.01, key='temperature')

# -----------------------------------------------------------------------------
