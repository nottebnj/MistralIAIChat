
# Streamlit
import streamlit as st
import streamlit_authenticator as stauth

# Mistral AI
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

# -----------------------------------------------------------------------------

# Page configuration
st.set_page_config(
    page_title="Mistral AI",
    page_icon=":gear:",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={}
)

# import yaml
# from yaml.loader import SafeLoader
# with open('../config.yaml') as file:
#     config = yaml.load(file, Loader=SafeLoader)

# hashed_passwords = stauth.Hasher(['abc']).generate()
# print(hashed_passwords)

# Basic config for authenticator
config = {
            'cookie': {'expiry_days': 1, 'key': st.secrets.auth_token_key, 'name': 'auth_token'},
            'credentials': {'usernames': {'guest': {'email': '', 'logged_in': False, 'name': 'Guest', 'password': st.secrets.password }}},
            'preauthorized': {'emails': []}
         }

# Authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Title
st.title(":gear: Mistral AI Chat")

# Login
authenticator.login()
if not st.session_state["authentication_status"]:
    if st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    st.stop()

# Session state
# Mistral AI Client
if not 'client' in st.session_state:
    st.session_state.client = MistralClient(api_key=st.secrets.api_key)
# History
if not 'history' in st.session_state:
    st.session_state.history = []
# Model
if not 'models' in st.session_state:
    client = st.session_state.client
    list_models_response = client.list_models()
    models = [ d.id for d in list_models_response.data ]
    if 'mistral-tiny' in models:
        models.remove('mistral-tiny')
        models.insert(0, 'mistral-tiny')
    st.session_state.models = models

# Model parameters
st.write('**Mistral AI model parameters**')
col1, col2, col3, col4 = st.columns([3, 3, 1, 1])
# Models
with col1:
    st.selectbox('Model ([info](https://mistral.ai/news/la-plateforme/))', st.session_state.models, index=0, key='model')
# Temperature slider
with col2:
    st.slider('Temperature', 0.0, 1.0, 0.7, 0.01, key='temperature')
# Clear button
with col3:
    if st.button("Restart", type="secondary"):
        st.session_state.history = []
# Logout
with col4:
    authenticator.logout()
st.divider()

# Discussion
for t, msg in st.session_state.history:
    if t=='Q':
        with st.chat_message("user"):
            st.write(f':blue[**{msg}**]')
    else:
        with st.chat_message("ai"):
            st.write(f'{msg}')

# Prompt
if prompt := st.chat_input("Ask for anything..."):
    if not (prompt is None or prompt==''):
        # Clean
        prompt = prompt.strip()
        with st.chat_message("user"):
            st.write(f':blue[**{prompt}**]')
        # History
        st.session_state.history.append(('Q', prompt))
        # Messages
        history = [ h[1] for h in st.session_state.history if h[0]=='Q' ]
        messages = [ ChatMessage(role="user", content=msg) for msg in history ]
        # Chat with streaming
        model = st.session_state.model
        temperature = st.session_state.temperature
        client = st.session_state.client
        chat_stream = client.chat_stream(model=model, messages=messages,
                                        max_tokens=None, temperature=temperature,
                                        top_p=None, safe_prompt=False, random_seed=None)
        # Response
        with st.chat_message("ai"):
            message_placeholder = st.empty()
            response =''
            for chunk in chat_stream:
                response += chunk.choices[0].delta.content
                message_placeholder.write(response + "▌")
            message_placeholder.write(response)
        # Update history
        st.session_state.history.append(('R', response))

# -----------------------------------------------------------------------------
