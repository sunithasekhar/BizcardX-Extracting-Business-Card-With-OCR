
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io


def image_to_text(path):
  input_img= Image.open(path)
  #convert image to array format
  image_arr=np.array(input_img)
  reader=easyocr.Reader(['en'])
  text=reader.readtext(image_arr,detail=0)
  return text,input_img


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
    elif "WWW" in texts[i] or "www" in texts[i]:
      small=texts[i].lower()
      extracted_dict["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extracted_dict["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]',texts[i])  :
      extracted_dict["COMPANY_NAME"].append(texts[i])

    else:
      remove_coln=re.sub(r'[,;]','',texts[i])
      extracted_dict["ADDRESS"].append(remove_coln)


  for key,value in extracted_dict.items():
    if len(value)>0:
      concatenate=" ".join(value)
      #print(concatenate)
      extracted_dict[key]=[concatenate]

    else:
      value="NA"
      extracted_dict[key]=[value]

    #print(key,":",value,len(value))

  return extracted_dict


#streamlit

st.set_page_config(layout="wide")
st.title("EXTRACTING BUSINESS CARD DATA WITH 'OCR'")
with st.sidebar:
  select=option_menu("main menu",["Home","Upload and modify","Delete"])
if select=="Home"  :
  pass

# elif select=="Upload and modify":
#   img=st.file_uploader("upload the image",type=["png","jpg","jpeg"])

#   if img is not None:
#     st.image(img,width=300)
#     text_image,input_img=image_to_text(img)
    
#     text_dict=extracted_text(text_image)
#     if text_dict: 
#       st.success("TEXT IS EXTRACTED SUCCESSFULLY")

#     df=pd.dataframee(text_dict)
    
    
    # #converting image to bytes

    # Image_bytes=io.BytesIO()
    # input_img.save(Image_bytes,format="PNG")

    # image_data=Image_bytes.getvalue()
    # image_data
    # #creating dictionary
    # data={"image":[image_data]}
    # df_1=pd.DataFrame(data)
    # concat_df=pd.concat([df,df_1],axis=0)
    # st.dataframe(concat_df)




elif select=="Delete"  :
  pass
