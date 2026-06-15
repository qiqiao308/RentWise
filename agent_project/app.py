import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from agent.react_agent import ReactAgent


st.title("智能租房客服")
st.divider ()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] =  []

for message in st.session_state["message"]:
    role = message["role"]
    st.chat_message(role).write(message["content"])

#用户输入提示词
prompt =st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []
    with st.spinner("思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator,cache_list):

            for chunk in generator:
                cache_list.append(chunk)


                for char in chunk:
                    time.sleep(0.01)
                    yield  char

        st.chat_message("assistant").write_stream(capture(res_stream,response_messages))
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        st.rerun ()