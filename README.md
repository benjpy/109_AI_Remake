# 🍌 AI Remake

AI Remake is a powerful Streamlit application that leverages Google's Gemini models to analyze, recreate, and refine images. It uses a sophisticated iterative process to generate high-quality AI reinterpretations of your uploaded photos.

## ✨ Features

-   **Deep Image Analysis**: Uses `gemini-2.5-flash` to extract a detailed, structured JSON description of your uploaded image.
-   **AI Image Generation**: Generates new images based on the analysis using `gemini-2.5-flash-image`.
-   **Iterative Refinement**: Features a "Refine Image" workflow that compares the generated result with the original source. It identifies discrepancies in proportions, layout, and details, then automatically rewrites the prompt to improve the next generation.
-   **History Tracking**: Keeps track of your refinement history, allowing you to view and download previous versions.
-   **Transparent Prompts**: View the exact JSON prompts used for generation to understand how the AI interprets your image.

## 🚀 Getting Started

### Prerequisites

-   Python 3.8+
-   A Google Cloud Project with the Gemini API enabled.
-   An API Key from [Google AI Studio](https://aistudio.google.com/).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd 109_AI_Remake
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your Gemini API key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```
    Alternatively, you can enter the API key directly in the application sidebar.

## 🛠️ Usage

1.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

2.  **Upload an Image:**
    -   Click "Browse files" to upload a JPG or PNG image.

3.  **Remake:**
    -   Click the **✨ Remake Image** button.
    -   The app will analyze the image and generate a new version.

4.  **Refine:**
    -   If the result isn't quite right, click **🔧 Refine Image**.
    -   The AI will critique its own work against the original and generate a better version.
    -   You can repeat this process multiple times.

5.  **Download:**
    -   Download any of the generated images using the "Download Image" buttons.

## 📦 Technologies

-   [Streamlit](https://streamlit.io/) - The web framework used.
-   [Google GenAI SDK](https://pypi.org/project/google-genai/) - For accessing Gemini models.
-   [Pillow (PIL)](https://python-pillow.org/) - For image processing.
-   [Python Dotenv](https://pypi.org/project/python-dotenv/) - For managing environment variables.
