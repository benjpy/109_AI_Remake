import streamlit as st
import os
import json
import io
from dotenv import load_dotenv
from google import genai
from PIL import Image

# Page Config
st.set_page_config(
    page_title="AI Remake",
    page_icon="🍌",
    layout="wide"
)

# Load Environment Variables
load_dotenv()

def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)

def analyze_image(client, image, example_structure):
    prompt = f"""
    Analyze this image and provide a detailed, structured JSON description.
    The output MUST be valid JSON.
    Follow this structure exactly:
    
    {example_structure}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image],
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error analyzing image: {e}")
        return None

def refine_prompt(client, source_img, generated_img, current_prompt_json):
    comparison_prompt = f"""
    You are an expert image generation prompt engineer.
    
    Image 1 is the SOURCE image (the goal).
    Image 2 is the GENERATED image (current attempt).
    
    The generated image was created using this JSON prompt:
    {json.dumps(current_prompt_json, indent=2)}
    
    Compare the two images. Identify key differences where the generated image fails to capture the source image's details.
    
    Pay specific attention to:
    1. **Relative Proportions**: Check the size of elements relative to each other (e.g., head size vs body, object size vs hand).
    2. **Spatial Layout & Positioning**: Check the exact position of elements (left, right, above, below, center). Are they in the correct quadrant?
    3. **Angles & Perspective**: Check the camera angle (high angle, low angle, eye level) and the angle of the subject/objects.
    4. **Key Details**: Specific colors, textures, lighting, and background elements.

    Your task is to REWRITE the JSON prompt to fix these issues and make the next generation look closer to the source.
    
    Return a JSON object with this structure:
    {{
        "changes": ["list", "of", "key", "changes", "made"],
        "new_prompt": {{ ... the full updated JSON prompt ... }}
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[comparison_prompt, source_img, generated_img],
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error refining prompt: {e}")
        return None

def generate_image_from_prompt(client, prompt_json, input_image=None):
    prompt_text = "Generate a photorealistic image based on this detailed description:\n\n" + json.dumps(prompt_json, indent=2)
    
    contents = [prompt_text]
    if input_image:
        contents.append(input_image)

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=contents
        )
        
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    return Image.open(io.BytesIO(image_bytes))
        return None
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None

# Sidebar
with st.sidebar:
    st.title("Configuration")
    
    # API Key Handling
    env_api_key = os.getenv("GEMINI_API_KEY")
    api_key = st.text_input(
        "Gemini API Key",
        value=env_api_key if env_api_key else "",
        type="password",
        help="Get your key from Google AI Studio"
    )
    
    st.info("Models used:\n- Analysis: `gemini-2.5-flash`\n- Generation: `gemini-2.5-flash-image`")

# Main Interface
st.title("🍌 AI Remake")
st.markdown("Upload an image to analyze its style and content, then generate a new AI version of it.")

# Session State Initialization
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'current_prompt' not in st.session_state:
    st.session_state.current_prompt = None
if 'refined_images' not in st.session_state:
    st.session_state.refined_images = [] # List of (image, prompt, changes)

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display Original
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        st.image(image, width="stretch")

    # Remake Button
    if st.button("✨ Remake Image", type="primary"):
        if not api_key:
            st.error("Please provide a Gemini API Key in the sidebar.")
        else:
            client = get_gemini_client(api_key)
            
            # Load example structure
            try:
                with open("prompt_example.txt", "r") as f:
                    example_structure = f.read()
            except FileNotFoundError:
                example_structure = "Provide a detailed JSON description of the image."

            # Step 1: Analyze
            with st.status("Analyzing image...", expanded=True) as status:
                st.write("Extracting details with Gemini 2.5 Flash...")
                prompt_json = analyze_image(client, image, example_structure)
                
                if prompt_json:
                    st.session_state.current_prompt = prompt_json
                    st.write("Prompt generated!")
                    
                    # Step 2: Generate
                    st.write("Generating new image with Gemini 2.5 Flash Image (Nano Banana)...")
                    generated_image = generate_image_from_prompt(client, prompt_json)
                    
                    if generated_image:
                        st.session_state.generated_image = generated_image
                        st.session_state.refined_images = [] # Reset refinements
                        status.update(label="Remake Complete!", state="complete", expanded=False)
                    else:
                        status.update(label="Generation Failed", state="error")
                else:
                    status.update(label="Analysis Failed", state="error")

    # Display Results
    if st.session_state.generated_image:
        with col2:
            st.subheader("Remade Image")
            st.image(st.session_state.generated_image, width="stretch")
            
            with st.expander("View Prompt"):
                st.json(st.session_state.current_prompt)
            
            # Download Button
            buf = io.BytesIO()
            st.session_state.generated_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="Download Image",
                data=byte_im,
                file_name="remade_image.png",
                mime="image/png"
            )

        # Refinement Section
        st.divider()
        st.subheader("Refine Result")
        
        if st.button("🔧 Refine Image"):
            if not api_key:
                st.error("Please provide a Gemini API Key.")
            else:
                client = get_gemini_client(api_key)
                
                # Determine which image to compare against (last refined or initial generated)
                current_gen_img = st.session_state.refined_images[-1][0] if st.session_state.refined_images else st.session_state.generated_image
                current_prompt = st.session_state.refined_images[-1][1] if st.session_state.refined_images else st.session_state.current_prompt

                with st.status("Refining image...", expanded=True) as status:
                    st.write("Comparing images and updating prompt...")
                    refinement_result = refine_prompt(client, image, current_gen_img, current_prompt)
                    
                    if refinement_result:
                        new_prompt = refinement_result.get("new_prompt")
                        changes = refinement_result.get("changes", [])
                        
                        st.write("Generating refined image...")
                        # Generate from the new prompt (Text-to-Image), not using the previous image as input
                        new_image = generate_image_from_prompt(client, new_prompt)
                        
                        if new_image:
                            st.session_state.refined_images.append((new_image, new_prompt, changes))
                            status.update(label="Refinement Complete!", state="complete", expanded=False)
                        else:
                            status.update(label="Generation Failed", state="error")
                    else:
                        status.update(label="Refinement Failed", state="error")

        # Display Refined Images
        if st.session_state.refined_images:
            st.markdown("### Refinement History")
            for i, (ref_img, ref_prompt, changes) in enumerate(reversed(st.session_state.refined_images)):
                with st.container():
                    st.markdown(f"**Refinement {len(st.session_state.refined_images) - i}**")
                    r_col1, r_col2 = st.columns([1, 2])
                    
                    with r_col1:
                        st.image(ref_img, width="stretch") # Fixed warning
                        # Download for refined
                        r_buf = io.BytesIO()
                        ref_img.save(r_buf, format="PNG")
                        r_byte_im = r_buf.getvalue()
                        st.download_button(
                            label=f"Download Refinement {len(st.session_state.refined_images) - i}",
                            data=r_byte_im,
                            file_name=f"refined_image_{len(st.session_state.refined_images) - i}.png",
                            mime="image/png",
                            key=f"dl_{i}"
                        )
                    
                    with r_col2:
                        st.markdown("**Changes Made:**")
                        for change in changes:
                            st.markdown(f"- {change}")
                        with st.expander("View Updated Prompt"):
                            st.json(ref_prompt)
                    st.divider()
