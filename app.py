import numpy as np
import pickle
import streamlit as st
from sklearn.preprocessing import StandardScaler,LabelEncoder
import psycopg2

# importing dataset and model
model=pickle.load(open('model.pkl','rb'))
data=pickle.load(open('df.pkl','rb'))

#background image
page_bg_img = '''
<style>
.stApp {

background-repeat: no-repeat;
background-size:100% 100%;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)


#background-image: url("C:/Users/annamalai/Downloads/img-unsplash.jpg");

   
# Title
st.title('Customer Churn Prediction'.upper())

# Credit Score
CreditScore=st.number_input(label='Credit Score',min_value=300,max_value=900)

# Geography
Geography=st.selectbox(label='Geography',options=data['Geography'].unique())

# Gender
Gender=st.selectbox(label='Gender',options=data['Gender'].unique())

# Age
Age=st.number_input(label='Age',min_value=1)

# Tenure
Tenure=st.number_input(label='Tenure',max_value=10,min_value=0)

# Balance
Balance=st.number_input(label='Balance')

# NumOfProducts
NumOfProducts=st.selectbox(label='NumOfProducts',options=data['NumOfProducts'].unique())

# Has Credit Card
HasCrCard=(lambda x:1 if x=='Yes' else 0)(st.selectbox(label='HasCreditCard',options=['Yes','No']))

# IsActiveMember
IsActiveMember=(lambda x:1 if x=='Yes' else 0)(st.selectbox(label='IsActiveMember',options=['Yes','No']))

# EstimatedSalary
EstimatedSalary=st.number_input(label='EstimatedSalary')

# scalling the column values
sc=StandardScaler()
columns=['CreditScore','Age','Balance','EstimatedSalary']
sc.fit_transform(data[columns])
features=list(sc.transform([[CreditScore,Age,Balance,EstimatedSalary]])[0])

# scalling the Tenure values
Tenure= (lambda x:0 if x>=0 and x<=5 else 1)(Tenure)

# Mapping the Tenure values
Gender= (lambda x:0 if x=='Female' else 1)(Gender)

# Mapping the Tenure values
Geography=(lambda x:0 if x=='Spain' or x=='France' else 1)(Geography)

if st.button('Predict'):
    query = list()
    query=[features[0],Geography,Gender,features[1],Tenure,features[2],NumOfProducts,HasCrCard,IsActiveMember,features[3]]
    ans = model.predict(np.array([query]))
    st.title("The Customer is predicted as " +(lambda x: 'Churned' if x==1 else 'Retained')(ans))
    print(ans[0])
    query.append(ans[0])
    print(query)

    conn = psycopg2.connect(host='annamalai.crhq093vjbni.ap-south-1.rds.amazonaws.com', dbname='postgres',
                        user='postgres', password='9894056344')
    cursor = conn.cursor()

    cursor.execute("""SELECT relname FROM pg_class WHERE relkind='r'
                  AND relname !~ '^(pg_|sql_)';""") # "rel" is short for relation.

    tables = [i[0] for i in cursor.fetchall()]


    if 'churn' not in tables:       
        command =   """
                        CREATE TABLE churn (
                            CreditScore SERIAL NOT NULL,
                            Geography SERIAL NOT NULL,
                            Gender SERIAL NOT NULL,
                            Age SERIAL NOT NULL,
                            Tenure SERIAL NOT NULL,
                            Balance SERIAL NOT NULL,
                            NumofProducts SERIAL NOT NULL,
                            HasCrCard SERIAL NOT NULL,
                            IsActiveMember SERIAL NOT NULL,
                           EstimatedSalary SERIAL NOT NULL,
                           Exited SERIAL NOT NULL
                        )
                        """
        cursor.execute(command)
            
        
    else:
          pass

    postgres_insert_query = """ INSERT INTO churn (CreditScore,Geography,Gender,Age,Tenure,Balance,NumofProducts,HasCrCard,IsActiveMember,EstimatedSalary,Exited) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    record_to_insert = tuple([np.float64(i) for i in query])
    print(record_to_insert)
    cursor.execute(postgres_insert_query, record_to_insert)  

    conn.commit()
    count = cursor.rowcount
    print(count, "Record inserted successfully into mobile table")    
                        
    
                

                

                

    

    

    
