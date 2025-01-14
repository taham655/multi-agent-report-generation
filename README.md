# Report Generator

A simple tool that helps you create well-structured reports without the hassle. It uses two smart agents working together to handle different parts of the report writing process.

## How it Works

The system follows a straightforward workflow (see diagram):

1. First, it reads your source documents (like PDFs) from a specified folder
2. Agent 1 (the delegation agent) creates an outline for your report
3. You can review and modify this outline until you're happy with it
4. Agent 2 (the writer agent) then writes each section based on the approved outline
5. You can review and revise each section before moving to the next
6. Finally, it saves everything as a nice Markdown file

The cool part is that you're always in control - both agents check with you before moving forward (that's the "human-in-the-loop" part in the diagram). This means you can fine-tune the report structure and content until it's exactly what you want.

## Setting Up

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API key:
   ```
   GEMINI_API_KEY=your_key_here
   ```
5. Put your source PDFs in a folder called "source"

## Using the Tool

1. Run the script:
   ```bash
   python main.py
   ```
2. The tool will:
   - Read your source documents
   - Suggest a report structure
   - Ask if you want to modify it
   - Write each section and check with you before moving forward
   - Save the final report as a Markdown file

## Tips

- When reviewing the structure, take your time to make sure it covers everything you need
- You can give specific feedback for each section if you want changes
- The final report is saved in Markdown format, so you can easily convert it to other formats later

## Requirements

- Python 3.8 or newer
- See requirements.txt for all Python packages needed

## Good to Know

- The tool saves your report with a timestamp, so you won't accidentally overwrite old versions
- Each section is generated based on your source documents, so make sure they contain all the info you need
- You can always go back and revise sections if they're not quite right

Found a bug or have a suggestion? Feel free to open an issue!
