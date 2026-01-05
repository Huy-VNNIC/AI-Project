"""Software Effort Estimation - Hugging Face Spaces App"""

import gradio as gr

def estimate_effort(text):
    """Simple effort estimation function"""
    if not text or len(text.strip()) < 5:
        return "Please provide some requirements text."
    
    words = text.split()
    word_count = len(words)
    
    # Simple estimation logic
    if word_count < 20:
        complexity = "Very Low"
        effort = 1.0
    elif word_count < 50:
        complexity = "Low" 
        effort = 2.0
    elif word_count < 100:
        complexity = "Medium"
        effort = 4.0
    elif word_count < 200:
        complexity = "High"
        effort = 8.0
    else:
        complexity = "Very High"
        effort = 12.0
    
    duration = effort * 0.75
    team_size = max(1, int(effort / duration))
    
    return f"""**📊 Estimation Results**

**Project Complexity**: {complexity}
**Word Count**: {word_count} words

**📈 Effort Estimation:**
• **Total Effort**: {effort:.1f} person-months
• **Duration**: {duration:.1f} months  
• **Team Size**: {team_size} people

**🎯 Confidence**: Medium

**Requirements**: "{text[:100]}..."
"""

def process_file(file):
    """Process uploaded file"""
    if not file:
        return "Please upload a file."
    
    try:
        with open(file.name, 'r', encoding='utf-8') as f:
            content = f.read()
        return estimate_effort(content)
    except Exception as e:
        return f"Error: {str(e)}"

# Create interface
with gr.Blocks(title="Software Effort Estimation") as demo:
    gr.HTML("<h1>🚀 Software Effort Estimation</h1>")
    
    with gr.Tabs():
        with gr.TabItem("📝 Text Analysis"):
            text_input = gr.Textbox(
                label="Requirements", 
                lines=6,
                value="Build a web app with user auth and dashboard"
            )
            text_btn = gr.Button("Analyze")
            text_output = gr.Markdown()
            text_btn.click(estimate_effort, text_input, text_output)
        
        with gr.TabItem("📄 File Upload"):
            file_input = gr.File(label="Upload File")
            file_btn = gr.Button("Process")
            file_output = gr.Markdown()
            file_btn.click(process_file, file_input, file_output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
