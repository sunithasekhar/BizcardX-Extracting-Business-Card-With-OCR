#The packages are imported
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

#define a function image_to_text with parameter path.
def image_to_text(path):
  input_img= Image.open(path) 
  #convert image to array format(numpy array)
  image_arr=np.array(input_img)
  reader=easyocr.Reader(['en'])
  text=reader.readtext(image_arr,detail=0)
  return text,input_img


#define a function extracted_text to return extracted_dict which contains the valid informatioin from the card and saved in dictionary format.

def extracted_text(texts):
  extracted_dict={"NAME":[],"DESIGNATION":[],"COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[],
                  "ADDRESS":[], "PINCODE":[]}

  extracted_dict["NAME"].append(texts[0])
  extracted_dict["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):
    if texts[i].startswith("+") or(texts[i].replace("-","").isdigit() and '-' in texts[i]):
      extracted_dict["CONTACT"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      extracted_dict["EMAIL"].append(texts[i])

        
    elif "www" in texts[i].lower():
      
      extracted_dict["WEBSITE"].append(texts[i])  
      

    match=re.search(r'\b\d{6}\b',texts[i])
    if match:
      extracted_dict["PINCODE"].append(match.group())
      

    elif re.match(r'^[A-Za-z]',texts[i]):
      extracted_dict["COMPANY_NAME"].append(texts[i])

    else:
      remove_coln=re.sub(r'[,;]','',texts[i])
      extracted_dict["ADDRESS"].append(remove_coln)


  for key,value in extracted_dict.items():
    if len(value)>0:
      concatenate=" ".join(value)
    
      extracted_dict[key]=[concatenate]

    else:
      value="NA"
      extracted_dict[key]=[value]

  return extracted_dict



#streamlit part


st.set_page_config(layout="wide")

st.title("BizcardX: Extracting Business Card Data With OCR")

with st.sidebar:
  select=option_menu("main menu",["Home","Upload and modify","Delete"])
  
if select=="Home":
  st.markdown("#### :blue[**Technologies Used:**] \n #### Python, easy OCR, Streamlit GUI, SQL, Pandas")
  
  st.write("#### :blue[**About BizcardX:**] \n #### BizcardX is a python application designed to extract buziness card details.The main purpose of BizcardX is to automate the process of extracting key details from business card images. The relevant information has been extracted from the uploaded image using easyOCR. The extracted information is then saved into a database. In this UI data can be modified and saved. Also there is an option to delete the unwanted data.")
  


elif select=="Upload and modify":
  img=st.file_uploader("upload the image",type=["png","jpg","jpeg"])

  if img is not None:
    st.image(img,width=300)
    text_image,input_img=image_to_text(img)
    text_dict=extracted_text(text_image)
    if text_dict:
      st.success("TEXT IS EXTRACTED SUCCESSFULLY")
      
    df=pd.DataFrame(text_dict)
    df.index=df.index+1

    #converting image to bytes

    Image_bytes=io.BytesIO()
    input_img.save(Image_bytes,format="PNG")

    image_data=Image_bytes.getvalue()
  
    #creating dictionary
    
    data={"image":[image_data]}
    df_1=pd.DataFrame(data)
    concat_df=pd.concat([df,df_1],axis=1)
    
    
    st.dataframe(concat_df)
    
    button_1=st.button("Save")
    
    if button_1:
      
      mydb=sqlite3.connect("bizcardx.db")
      cursor=mydb.cursor()

      #table creation
      create_table_query='''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(230),
                                                                      designation varchar(225),
                                                                      company_name varchar(230),
                                                                      contact varchar(230),
                                                                      email varchar(230),
                                                                      website text,
                                                                      address text,
                                                                      pincode varchar(230),
                                                                      image text)'''

      cursor.execute(create_table_query)                                                                 
      mydb.commit()
      #mydb.close()
      
      
      #insert query
      insert_query='''INSERT INTO bizcard_details(name,designation,company_name,contact,email,website,address,pincode,image)
                
                      values(?,?,?,?,?,?,?,?,?)'''


      datas=concat_df.values.tolist()[0]
      cursor.execute(insert_query,datas) 
      mydb.commit()     
      
      
      st.success("saved successfully") 
      



  method=st.radio("select the method",["None","Preview","Modify"])
  
  if method=="None":
    st.write("  ")
  if method=="Preview":
    
    mydb=sqlite3.connect("bizcardx.db")
    cursor=mydb.cursor()
    
    select_query="SELECT * FROM bizcard_details"
    cursor.execute(select_query)
    table=cursor.fetchall()
    mydb.commit()
    

    table_df=pd.DataFrame(table, columns=("NAME","DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))
    table_df.index=table_df.index+1
    st.dataframe(table_df)
    
    #remove duplicate entries. If more than one entries exist with same name, desifgnation and contact it is removed.
    
    table_df = table_df.drop_duplicates(subset=["NAME", "DESIGNATION", "CONTACT"])
    
    table_df = table_df.drop_duplicates(subset="NAME")
    
  elif method=="Modify":
    mydb=sqlite3.connect("bizcardx.db")
    cursor=mydb.cursor()
    
    select_query="SELECT * FROM bizcard_details"
    cursor.execute(select_query)
    table=cursor.fetchall()
    mydb.commit()

    table_df=pd.DataFrame(table, columns=("NAME","DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"))
    
    
    column1,column2=st.columns(2)
    
    
    with column1:
      selected_name=st.selectbox("select the name", table_df["NAME"])
      
      
    df_3=table_df[table_df["NAME"]==selected_name]
    
    st.dataframe(df_3)
     
    df_4=df_3.copy()
    
    df_4.index=df_4.index+1
    
    st.dataframe(df_4)
    
    col1,col2=st.columns(2)
    
    with col1:
      mo_name=st.text_input("Name",df_3["NAME"].unique()[0])
      mo_desig=st.text_input("designaton",df_3["DESIGNATION"].unique()[0])
      mo_com_name=st.text_input("company_name",df_3["COMPANY_NAME"].unique()[0])
      mo_contact=st.text_input("contact",df_3["CONTACT"].unique()[0])
      mo_email=st.text_input("email",df_3["EMAIL"].unique()[0])
      
      df_4["NAME"]=mo_name
      df_4["DESIGNATION"]=mo_desig
      df_4["COMPANY_NAME"]=mo_com_name
      df_4["CONTACT"]=mo_contact
      df_4["EMAIL"]=mo_email
    
    
      
    with col2:
       mo_website=st.text_input("website",df_3["WEBSITE"].unique()[0]) 
       mo_address=st.text_input("address",df_3["ADDRESS"].unique()[0]) 
       mo_pincode=st.text_input("pincode",df_3["PINCODE"].unique()[0])
       mo_image=st.text_input("image",df_3["IMAGE"].unique()[0])
       
       
       df_4["WEBSITE"]=mo_website
       df_4["ADDRESS"]=mo_address
       df_4["PINCODE"]=mo_pincode
       df_4["IMAGE"]=mo_image 
       
       
       df_4.index=df_4.index+1   
    
    
    st.dataframe(df_4) 
    
    
    table_df = table_df.drop_duplicates(subset=["NAME", "DESIGNATION", "CONTACT"])
    
    
    col1,col2=st.columns(2)
    with col1:
      button_3=st.button("Modify", use_container_width=True)
      
    if button_3:
      mydb=sqlite3.connect("bizcardx.db")
      cursor=mydb.cursor()
      
      
      cursor.execute(f"DELETE FROM bizcard_details WHERE NAME='{selected_name}'")
      
      mydb.commit()
      
      
      #insert query
      
      insert_query='''INSERT INTO bizcard_details(name,designation,company_name,contact,email,website,address,pincode,image)
                
                      values(?,?,?,?,?,?,?,?,?)'''

      df_4.index=df_4.index+1
      df_4
      datas=df_4.values.tolist()[0]
      cursor.execute(insert_query,datas) 
      mydb.commit()     
      
         
      st.success("modified successfully") 
      
            

elif select=="Delete":
  
  mydb=sqlite3.connect("bizcardx.db")
  cursor=mydb.cursor()
  
  col1,col2=st.columns(2)
  
  with col1:
    
    select_query="SELECT NAME FROM bizcard_details"
    cursor.execute(select_query)
    table1=cursor.fetchall()
    mydb.commit()
    
    names=[]
    for i in table1:
      names.append(i[0])
      
    name_select=st.selectbox("select the name",  names)
    
  with col2:
  
    select_query=f"SELECT DESIGNATION FROM bizcard_details WHERE NAME ='{name_select}'"
    cursor.execute(select_query)
    table2=cursor.fetchall()
    mydb.commit()
    
    designation=[]
    for j in table2:
      designation.append(j[0])
      
    designation_select=st.selectbox("select the designation",designation)  
    
    
  if name_select and designation_select:
  
    col1,col2,col3=st.columns(3)
  
    with col1: 
      st.write(f"selected name: {name_select}")
      st.write("")
      st.write("")
      st.write("")
      st.write(f"selected_dsignation: {designation_select}")
      
    with col2:
      st.write("")  
      st.write("")
      st.write("")
      st.write("")
      remove=st.button("DELETE", use_container_width=True)
      
      if remove:
      
        cursor.execute(f"DELETE FROM bizcard_details WHERE NAME='{name_select}' AND DESIGNATION= '{designation_select}'")
        
        mydb.commit()
        
        st.warning("DELETED")
      
    
    
    
    
      
    
  

