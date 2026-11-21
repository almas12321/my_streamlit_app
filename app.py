import streamlit as st

st.title("Registration Form")

with st.form("Important Information"):
    name = st.text_input("Enter your name*")
    salary = st.number_input("Enter your salary*",min_value=10000,max_value=50000,step=10000,)
    #age = st.slider("Enter your age",min_value=1,max_value=100)
    age = st.number_input("Enter your age",min_value=1,max_value=100)
    
    gender = st.selectbox("Enter your gender (optional)",["Male","Female"])


    submitted = st.form_submit_button()
    if submitted:
        st.write("Form submitted successfully")
        if not name.strip():
            st.error("Kindly fill the name field")
        #elif not age:
            #st.error("kindly fill the age")
        elif not gender:
                    st.error("Enter your gender")
        else:
              st.write(f"my name is : {name} ")
              st.write(f"my age is : {age}")
              st.write(f"my gender is : {gender}")