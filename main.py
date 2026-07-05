import streamlit as st
from auth import authenticate

def main():
    st.set_page_config(
        page_title="Analisis Produktivitas Padi",
        page_icon="🌾",
        layout="wide"
    )

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate()
    else:
        st.sidebar.title("Analisis Produktivitas Padi")
        st.sidebar.success(f"Selamat datang, {st.session_state.username}!")
        
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

if __name__ == "__main__":
    main()