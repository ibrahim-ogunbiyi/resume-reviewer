from lib.llm import llm
from langchain_core.prompts import ChatPromptTemplate

# llm.invoke(

# ) 



def fit_to_job_description():

    prompt =  ChatPromptTemplate.from_messages(
    [
        (
            "system",
            
        ),

        ("human", "{resume}", "{job_description}")

    ]
    )

    chain =  prompt | llm

    chain.invoke(

        {
            "resume": "None",
            "job_description": "None"
        }
    )      

