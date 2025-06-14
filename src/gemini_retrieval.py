from google import genai
import os

def return_gemini_response(query: str, current_run_path: str, model: str = "gemini-2.5-flash-preview-05-20"):
    
    client = genai.Client(api_key="AIzaSyC0i9vw1GMG9EYvmSjbamqCsSK-d-sdyA4")


        
    filtered_posts = client.files.upload(file = os.path.join(current_run_path, f"vector_search_results.txt"))

    response = client.models.generate_content(
        model=model,
        contents=[query, filtered_posts]
    )

    with open(os.path.join(current_run_path, f"gemini_response.txt"), "w") as file:
        file.write(response.text)
    
    
