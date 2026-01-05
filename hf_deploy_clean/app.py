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

# Create simple interface
demo = gr.Interface(
    fn=estimate_effort,
    inputs=gr.Textbox(
        lines=6,
        placeholder="Enter your software requirements here...",
        label="Project Requirements"
    ),
    outputs=gr.Markdown(label="Estimation Results"),
    title="🚀 Software Effort Estimation",
    description="Estimate software development effort from project requirements",
    examples=[
        ["Build a web app with user authentication and dashboard"],
        ["Create a mobile app for e-commerce with payment integration"],
        ["Develop a REST API with database integration and user management"]
    ]
)

if __name__ == "__main__":
    demo.launch()