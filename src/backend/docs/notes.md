conda create --name rural_healthcare_navigator_env  
conda env list  
conda activate rural_healthcare_navigator_env  
python --version  
conda install python=3.9  

pip install \
langgraph \
langchain \
langchain-openai \
langchain-community \
qdrant-client \
fastapi \
uvicorn \
python-dotenv \ 
beautifulsoup4 
langchain-qdrant 
uvicorn app.main:app --reload\
streamlit run streamlit_app.py

beautifulsoup4 for webbaseloader