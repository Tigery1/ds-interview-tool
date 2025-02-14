from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval # enables execution of JavaScript commands in the browser

# Set up the page
st.set_page_config(page_title='Streamlit Chat', page_icon="💬")
st.title('Chatbot')

# Initialize session state variable to track setup completion
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

# Set up a message count variable to track the number of messages exchaged
if 'user_message_count' not in st.session_state:
    st.session_state.user_message_count = 0

# Initialize a feedback variable to indicate whether or not the user has been shown feedback for the interview
if 'feedback_shown' not in st.session_state:
    st.session_state.feedback_shown = False

# Define a function to set the setup phase completion status to True
# Later, this will be attached to a button using an 'on_click' event, so the function will run when the button is clicked.


def complete_setup():
    st.session_state.setup_complete = True

# Define a function to set the feedback_shown status to True


def show_feedback():
    st.session_state.feedback_shown = True


# Show the setup form only if setup is incomplete
if not st.session_state.setup_complete:

    # Indicate where user input will be stored
    st.subheader('Personal Information')

    # Initialize session state variables for the user's personal information
    # This enables tracking of data across different sessions, and ensures the data is persistent within each session
    if 'name' not in st.session_state:
        st.session_state['name'] = ''
    if 'experience' not in st.session_state:
        st.session_state['experience'] = ''
    if 'skills' not in st.session_state:
        st.session_state['skills'] = ''
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chat_complete' not in st.session_state:
        st.session_state.chat_complete = False

    # Test labels for personal information
    st.session_state['name'] = st.text_input(label='Name', max_chars=40, value=st.session_state['name'],
                                             placeholder='Enter your name')

    st.session_state['experience'] = st.text_area(label='Experience', value=st.session_state['experience'], height=None, max_chars=200,
                                                  placeholder="Describe your experience")

    st.session_state['skills'] = st.text_area(label='Skills', value=st.session_state['skills'], height=None, max_chars=None,
                                              placeholder='List your skills')

    st.write(f"**Your Name**: {st.session_state['name']}")
    st.write(f"**Your Experience**: {st.session_state['experience']}")
    st.write(f"**Your Skills**: {st.session_state['skills']}")

    # Custom Divider with Orange and Black Stripes using HTML
    divider = """
        <hr style="border: 0; border-top: 5px dashed orange; border-bottom: 5px dashed black; margin-top: 20px; margin-bottom: 20px;">
    """

    st.subheader('Company and Position')
    st.markdown(divider, unsafe_allow_html=True)

    # Set default sessions state status for level, position, and company
    if 'level' not in st.session_state:
        st.session_state['level'] = 'Junior'
    if 'position' not in st.session_state:
        st.session_state['position'] = 'Data Scientist'
    if 'company' not in st.session_state:
        st.session_state['company'] = 'Amazon'

    col1, col2 = st.columns(2)
    with col1:
        st.session_state['level'] = st.radio(  # add radio buttons
            'Choose level',
            key='visibility',
            options=['Junior', 'Mid-level', 'Senior'],
        )

    with col2:
        st.session_state['position'] = st.selectbox(
            'Choose a position',
            ('Data Scientist', 'Data engineer',
             'ML Engineer', 'BI Analyst', 'Financial Analyst')
        )

    st.session_state['company'] = st.selectbox(
        'Choose a Company',
        ['Amazon', 'Meta', 'Udemy', '365 Company', 'Nestle', 'LinkedIn',
         'Spotify']
    )

    st.write(
        f"**Your information: {st.session_state['level']} {st.session_state['position']} at {st.session_state['company']}")

    # Call the complete_setup function when the 'Start Interview' button is clicked
    if st.button('Start Interview', on_click=complete_setup):
        st.write('Setup complete. Starting interview...')

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info(
        '''
        Start by introducting yourself.''',
        icon='👋'
    )

   
    # Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])

    # Setting OpenAI model if not already initialized
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    # Initializing the system prompt for the chatbot
    if not st.session_state.messages:
        st.session_state.messages = [{
        "role": "system",
        "content": (f"You are an HR executive that interviews an interviewee called {st.session_state['name']} "
                   f"with experience {st.session_state['experience']} and skills {st.session_state['skills']}. "
                    f"You should interview him for the position {st.session_state['level']} {st.session_state['position']} "
                    f"at the company {st.session_state['company']}")
        }]

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Handle user input and OpenAI response
    # Put a max_chars limit
    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Your response", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})

            # Increment the user message count
            st.session_state.user_message_count += 1

    # Check if the user message count reaches 5
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

# Show "Get Feedback" 
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

# Show feedback screen
if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    # Initialize new OpenAI client instance for feedback
    feedback_client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])

    # Generate feedback using the stored messages and write a system prompt for the feedback
    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a helpful tool that provides feedback on an interviewee performance.
             Before the Feedback give a score of 1 to 10.
             Follow this format:
             Overal Score: //Your score
             Feedback: //Here you put your feedback
             Give only the feedback do not ask any additional questins.
              """},
            {"role": "user", "content": f"This is the interview you need to evaluate. Keep in mind that you are only a tool. And you shouldn't engage in any converstation: {conversation_history}"}
        ]
    )

    st.write(feedback_completion.choices[0].message.content)

    # Button to restart the interview
    if st.button("Restart Interview", type="primary"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
