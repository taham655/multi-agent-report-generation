from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, Field
from rich.prompt import Prompt
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage
from langchain_community.document_loaders import PyPDFDirectoryLoader
from dotenv import load_dotenv
import datetime

load_dotenv()


class SubSection(BaseModel):
    """Structure for a subsection of the report"""
    title: str
    content: Optional[str] = None

class ReportSection(BaseModel):
    """Structure for a section of the report"""
    title: str
    content: Optional[str] = None
    subsections: List[SubSection] = Field(default_factory=list)

class ReportStructure(BaseModel):
    """Overall structure of the report"""
    title: str
    sections: List[ReportSection]
    abstract: Optional[str] = None

class ReportContent(BaseModel):
    """Final report content"""
    structure: ReportStructure
    content: str

@dataclass
class Deps:
    source_documents: List[str]
    topic: str
    additional_context: Optional[str] = None

# Delegation agent responsible for structuring the report
delegation_agent = Agent[Deps, ReportStructure](
    'gemini-1.5-flash',
    result_type=ReportStructure,
    retries=2,
    system_prompt=(
        'You are a delegation agent responsible for creating report structures. '
        'Based on the topic and source documents, create a logical report structure. '
        'Consider academic report standards and ensure completeness.'
    ),
)

# Writer agent responsible for writing individual sections
writer_agent = Agent[Deps, str](
    'gemini-1.5-flash',
    result_type=str,
    retries=2,
    system_prompt=(
        'Write comprehensive, well-researched content based on the provided sources. '
        'Maintain academic writing standards and ensure proper citations.'
        'You will give harvard style citations for the sources you use, only use the sources you have been given'
        'You will give a reference section at the end of the report with the sources you have used'
        'Use the context you have been given to write the report, and cite the sources you have been provided nothing else'

    ),
)

@delegation_agent.tool
async def suggest_structure(ctx: RunContext[Deps]) -> ReportStructure:
    """Generate initial report structure based on topic and sources."""
    structure = ReportStructure(
        title=ctx.deps.topic,
        sections=[
            ReportSection(title="Abstract"),
            ReportSection(title="Introduction"),
            ReportSection(title="Background"),
            ReportSection(title="Methodology"),
            ReportSection(title="Results"),
            ReportSection(title="Discussion"),
            ReportSection(title="Conclusion")
        ]
    )
    return structure

async def generate_report(source_docs: List[str], topic: str, context: Optional[str] = None) -> ReportContent:
    deps = Deps(
        source_documents=source_docs,
        topic=topic,
        additional_context=context
    )

    message_history: Optional[List[ModelMessage]] = None
    final_structure: Optional[ReportStructure] = None

    # Structure refinement loop with human feedback
    while True:
        result = await delegation_agent.run(
            f"Create a report structure for topic: {topic}",
            deps=deps,
            message_history=message_history
        )

        print("\nProposed Report Structure:")
        print_structure(result.data)

        answer = Prompt.ask(
            'Do you accept this structure? (accept/modify)',
            choices=['accept', 'modify'],
            show_choices=True
        )

        if answer == 'accept':
            final_structure = result.data
            break
        else:
            feedback = input("Please provide feedback for revision: ")
            result = await delegation_agent.run(
                f"Revise the report structure based on feedback: {feedback}, this is currently the structure: {result.data}",
                deps=deps,
                message_history=result.all_messages()
            )

            print("\nProposed Report Structure:")
            print_structure(result.data)
            answer = Prompt.ask(
            'Do you accept this structure? (accept/modify)',
            choices=['accept', 'modify'],
            show_choices=True
            )

            if answer == 'accept':
              final_structure = result.data
              break


    # Generate content section by section
    complete_report = ""
    for section in final_structure.sections:
        print(f"\nGenerating content for section: {section.title}")
        section_content = await writer_agent.run(
            f"Write the {section.title} section for the report on {topic} make sure you use the sources {source_docs} and only use the sources you have been given and cite them in harvard style",
            deps=deps
        )

        # Show content to user for approval
        print(f"\nDraft content for {section.title}:")
        print(section_content.data)

        while True:
            answer = Prompt.ask(
                'Do you accept this section? (accept/revise)',
                choices=['accept', 'revise'],
                show_choices=True
            )

            if answer == 'accept':
                complete_report += f"\n\n# {section.title}\n\n{section_content.data}"
                break
            else:
                feedback = input("Please provide feedback for revision: ")
                section_content = await writer_agent.run(
                    f"Revise the {section.title} section based on feedback: {feedback}",
                    deps=deps,
                    message_history=section_content.all_messages()
                )
                print("\nRevised content:")
                print(section_content.data)

    return ReportContent(
        structure=final_structure,
        content=complete_report
    )

def print_structure(structure: ReportStructure, indent: int = 0):
    """Helper function to print report structure"""
    print("  " * indent + f"Title: {structure.title}")
    for section in structure.sections:
        print("  " * (indent + 1) + f"- {section.title}")
        for subsection in section.subsections:
            print("  " * (indent + 2) + f"  - {subsection.title}")

async def main():
    # Load PDF documents from source directory
    directory_path = "source"
    loader = PyPDFDirectoryLoader(directory_path)
    docs = loader.load()

    # Extract source documents from the loaded PDFs
    source_docs = []
    for doc in docs:
        source_docs.append(doc)


    topic = """Writing a progress report for my final year project. The project is called Jarvis which is a multi agent architecture
    with Human like memory to be a super useful personal assistant and have the ability to perform tasks as well.
    Multi-Modal Interaction: The system supports both text-based and voice-based interaction,
    accommodating diverse user preferences and contexts through integrated speech recognition
    and synthesis technologies.
    Platform and Device Integration: The implementation provides seamless integration with
    popular applications and services, including messaging platforms (e.g., Discord, email),
    mobile applications, and potential augmented reality interfaces, requiring platform-specific
    API development and integration modules.
    Natural Language Interface: The system prioritizes natural language interaction, enabling
    conversational communication while minimizing specific command requirements, leveraging
    advances in natural language understanding and generation """

    print("Starting report generation process...")
    report = await generate_report(source_docs, topic)

    # Save the report
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.md"
    with open(filename, "w") as f:
        f.write(report.content)

    print(f"\nReport has been saved to {filename}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())