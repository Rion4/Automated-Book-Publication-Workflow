from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

import config
from ChromaDB import ChromaDBManager
from scraper_agent import ScraperAgent
from writer_agent import WriterAgent
from reviewer_agent import ReviewerAgent
import voice_interface

console = Console()

def print_header():
    console.print(Panel("[bold magenta]Automated Book Publication Workflow[/bold magenta]", 
                        title="[cyan]Welcome[/cyan]", 
                        subtitle="[green]Powered by Gemini & ChromaDB[/green]"))

def run_scraper_stage(db_manager: ChromaDBManager):

    console.print("\n[bold yellow]Stage 1: Web Content Ingestion[/bold yellow]")
    scraper = ScraperAgent()
    content, screenshot, score = scraper.run(config.TARGET_URL)

    if content:
        console.print(f"[green]Scraping successful! Score: {score:.2f}[/green]")
        console.print(f"Screenshot saved to: '{screenshot}'")
        
        metadata = {"version": 1, "status": "original", "score": f"{score:.2f}"}
        db_manager.store_version(content, metadata)
    else:
        console.print("[bold red]Scraping failed. Exiting workflow.[/bold red]")
        exit()

def run_writer_stage(db_manager: ChromaDBManager, feedback: str = None):
    console.print("\n[bold yellow]Stage 2: AI Writer Agent[/bold yellow]")
    
    # Get the latest version to work on
    meta, text, doc_id = db_manager.get_latest_version()
    if not text:
        console.print("[bold red]Could not retrieve text for writer. Exiting.[/bold red]")
        exit()

    console.print(f"Rewriting version {meta.get('version', 'N/A')}...")
    writer = WriterAgent()
    spun_text = writer.run(text, human_feedback=feedback)

    if spun_text:
        console.print("[green]AI Writer finished.[/green]")
        new_version = meta.get('version', 0) + 1
        metadata = {
            "version": new_version,
            "status": "spun",
            "source_version": meta.get('version', 'N/A')
        }
        db_manager.store_version(spun_text, metadata)
    else:
        console.print("[bold red]AI Writer failed. Exiting workflow.[/bold red]")
        exit()

def run_reviewer_stage(db_manager: ChromaDBManager):

    console.print("\n[bold yellow]Stage 3: AI Reviewer Agent[/bold yellow]")
    
    meta, text, doc_id = db_manager.get_latest_version()
    if not text:
        console.print("[bold red]Could not retrieve text for reviewer. Exiting.[/bold red]")
        exit()

    console.print(f"Reviewing version {meta.get('version', 'N/A')}...")
    reviewer = ReviewerAgent()
    feedback, revised_text = reviewer.run(text)

    if feedback and revised_text:
        console.print("[green]AI Reviewer finished.[/green]")
        console.print(Panel(feedback, title="[cyan]Reviewer's Feedback[/cyan]"))
        
        new_version = meta.get('version', 0) + 1
        metadata = {
            "version": new_version,
            "status": "reviewed",
            "source_version": meta.get('version', 'N/A'),
            "review_notes": feedback
        }
        db_manager.store_version(revised_text, metadata)
    else:
        console.print("[bold red]AI Reviewer failed. Exiting workflow.[/bold red]")
        exit()

def run_human_in_the_loop(db_manager: ChromaDBManager):

    console.print("\n[bold yellow]Stage 4: Human-in-the-Loop (HITL)[/bold yellow]")
    meta, text, doc_id = db_manager.get_latest_version()
    
    if not text:
        console.print("[bold red]Nothing to review. Exiting.[/bold red]")
        return False 

    console.print(Panel(text, title=f"[cyan]Version {meta.get('version')} | Status: {meta.get('status').upper()}[/cyan]"))
    
    # Use voice to ask the user for their action
    action_prompt = "What would you like to do? Choose 'approve', 'edit', 'rewrite', or 'quit'."
    choice = Prompt.ask(action_prompt, choices=["approve", "edit", "rewrite", "quit"], default="approve")

    if choice == "approve":
        console.print("[bold green]Chapter Approved! Workflow complete.[/bold green]")
        return False 
    
    elif choice == "edit":
        console.print("[cyan]Please enter your edits. Type 'END' on a new line to save.[/cyan]")
        lines = []
        while True:
            line = input()
            if line == "END":
                break
            lines.append(line)
        edited_text = "\n".join(lines)
        new_version = meta.get('version', 0) + 1
        metadata = {
            "version": new_version, 
            "status": "human_edited",
            "source_version": meta.get('version')
        }
        db_manager.store_version(edited_text, metadata)
        console.print("[green]Your edits have been saved as a new version.[/green]")
        return True 

    elif choice == "rewrite":
        feedback_prompt = "Please provide feedback for the AI Writer. You can speak or type."
        use_voice = Confirm.ask("Use voice for feedback?", default=True)
        if use_voice:
            feedback = voice_interface.listen_for_input(prompt=feedback_prompt)
        else:
            feedback = Prompt.ask(feedback_prompt)
        
        if feedback:
            run_writer_stage(db_manager, feedback=feedback)
            run_reviewer_stage(db_manager) 
        else:
            console.print("[yellow]No feedback provided. Returning to options.[/yellow]")
        return True 

    elif choice == "quit":
        console.print("[bold magenta]Exiting workflow.[/bold magenta]")
        return False 
    
    return True

def run_semantic_search(db_manager: ChromaDBManager):

    console.print("\n[bold yellow]Bonus Stage: Semantic Search[/bold yellow]")
    if not Confirm.ask("Do you want to search the content archive?", default=True):
        return

    query_prompt = "What are you looking for? (e.g., 'a scene about a conflict')"
    use_voice = Confirm.ask("Use voice for search query?", default=False)
    if use_voice:
        query = voice_interface.listen_for_input(prompt=query_prompt)
    else:
        query = Prompt.ask(query_prompt)

    if query:
        results = db_manager.semantic_search(query)
        if results:
            console.print(f"\n[bold green]Found {len(results)} results for '{query}':[/bold green]")
            for res in results:
                console.print(Panel(
                    f"[dim]{res['content']}[/dim]\n\n[bold]Match Score (Distance):[/bold] {res['distance']}",
                    title=f"[cyan]ID: {res['id']} | Version: {res['metadata'].get('version')} | Status: {res['metadata'].get('status')}[/cyan]",
                    border_style="blue"
                ))
        else:
            console.print("[yellow]No relevant results found.[/yellow]")

def main():
    print_header()
    
    if not config.GOOGLE_API_KEY:
        console.print("[bold red]Error: GOOGLE_API_KEY is not set.[/bold red]")
        console.print("Please create a '.env' file and add your key.")
        return

    db_manager = ChromaDBManager()

    latest_meta, _, _ = db_manager.get_latest_version()
    if latest_meta and Confirm.ask("\n[bold]Previous work found. Continue from the latest version?[/bold]", default=True):
        console.print(f"Resuming workflow from version {latest_meta.get('version')}.")
    else:
        if latest_meta:
            console.print("Starting workflow from scratch...")
        run_scraper_stage(db_manager)
        run_writer_stage(db_manager)
        run_reviewer_stage(db_manager)

    while run_human_in_the_loop(db_manager): #Human Interaction
        pass 

    run_semantic_search(db_manager)
    
    console.print("\n[bold magenta]Workflow finished. Goodbye![/bold magenta]")


if __name__ == "__main__":
    main()
