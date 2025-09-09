from pathlib import Path

import streamlit as st

from lib.model import ModelClass
from services.fit_to_job_description import fit_to_job_description
from services.schema import FileSchema

ModelClass().load_models()

st.title("Resume Review: Tailor Resume to Job Description")

uploaded_file = st.file_uploader(label="Upload File", type=["pdf", "docx", "doc"])
job_description = st.text_area(label="Enter or Paste Job Description")

result = None
if uploaded_file and job_description:
    doc_bytes = uploaded_file.getvalue()
    file_extension = Path(uploaded_file.name).suffix
    file = FileSchema(doc_bytes=doc_bytes, ext=file_extension)
    result, ats_checker_result = fit_to_job_description(file=file, job_description=job_description)

if st.button("Process"):
    with st.spinner("Processing... ⏳"):
        if result:
            st.header("📋 Resume Review")
            for check in result["checks"]:
                with st.expander(f"🔹 {check['pillar']}"):
                    st.markdown(f"**🚨 Problem:** {check['problem']}")
                    st.markdown(f"**✅ Recommendation:** {check['recommendation']}")
        if ats_checker_result:
            st.success(f"ATS Score is {ats_checker_result[0]}")
            st.markdown(ats_checker_result[1])
