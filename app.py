import streamlit as st

st.set_page_config(page_title="PokéX IA", layout="wide")
st.markdown("<h1 style='text-align:center;color:#FF6B6B'>🤖 PokéX Games IA Chat</h1>", unsafe_allow_html=True)

pokex_kb = {
    "shiny": "Shiny 1/1000 Rota 1 + Lucky Egg",
    "mega": "Mega Pedras Cerulean Cave Raids Lv5+",
    "pvp": "Meta: MegaGyarados + CharY + Venusaur",
    "ivs": "IV 31/31/31 = perfeito. Checker PC"
}

if "msg" not in st.session_state:
    st.session_state.msg = [{"role": "ai", "text": "👋 Pergunte sobre PokéX!"}]

for m in st.session_state.msg:
    with st.chat_message(m["role"]):
        st.markdown(m["text"])

q = st.chat_input("💭 Sua dúvida...")
if q:
    st.session_state.msg.append({"role": "user", "text": q})
    with st.chat_message("user"): st.markdown(q)
    
    r = "❓ Tente: shiny, mega, pvp, ivs"
    for k,v in pokex_kb.items():
        if k in q.lower(): r = v
    with st.chat_message("ai"): st.markdown(r)
    st.session_state.msg.append({"role": "ai", "text": r})
