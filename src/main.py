#!/usr/bin/env python3
"""
Outlook AI Manager - LLM-powered email management system
"""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

from src.config.settings import settings
from src.auth.microsoft_auth import MicrosoftAuthenticator
from src.email.email_interface import EmailInterface
from src.llm.classifier import EmailClassifier
from src.actions.outlook_actions import EmailActions

console = Console()

@click.group()
def cli():
    """Outlook AI Manager - Intelligent email management system"""
    pass

@cli.command()
def gmail_setup():
    """Set up Gmail API credentials"""
    console.print("[bold blue]Gmail API Setup Guide[/bold blue]")
    
    console.print("\n[cyan]📋 Step-by-Step Gmail Setup:[/cyan]")
    
    console.print("\n[bold]Step 1: Create Google Cloud Project[/bold]")
    console.print("1. Go to https://console.cloud.google.com")
    console.print("2. Create a new project or select existing one")
    console.print("3. Enable the Gmail API")
    
    console.print("\n[bold]Step 2: Create Credentials[/bold]")
    console.print("1. Go to 'Credentials' in the left sidebar")
    console.print("2. Click '+ CREATE CREDENTIALS' → 'OAuth client ID'")
    console.print("3. Choose 'Desktop application'")
    console.print("4. Download the JSON credentials file")
    
    console.print("\n[bold]Step 3: Setup Your Project[/bold]")
    console.print("1. Save the downloaded file as 'credentials.json' in your project root")
    console.print("2. Update your .env file:")
    console.print("   [bold]EMAIL_PROVIDER=gmail[/bold]")
    console.print("   [bold]GMAIL_ADDRESS=your_gmail@gmail.com[/bold]")
    console.print("   [bold]TARGET_EMAIL=your_gmail@gmail.com[/bold]")
    
    console.print("\n[bold]Step 4: Test Setup[/bold]")
    console.print("Run: [bold]uv run outlook-ai setup[/bold]")
    
    # Check current status
    console.print("\n[cyan]📊 Current Status:[/cyan]")
    if settings.email_provider == "gmail":
        console.print(f"   Email provider: [green]gmail[/green]")
        if settings.has_gmail_credentials:
            console.print(f"   Credentials file: [green]✓ Found[/green]")
        else:
            console.print(f"   Credentials file: [red]✗ Not found[/red]")
        
        if settings.gmail_address:
            console.print(f"   Gmail address: [green]{settings.gmail_address}[/green]")
        else:
            console.print(f"   Gmail address: [red]✗ Not configured[/red]")
    else:
        console.print(f"   Email provider: [yellow]{settings.email_provider}[/yellow] (switch to gmail in .env)")

@cli.command()
def setup():
    """Initial setup and authentication test"""
    console.print("[bold blue]Outlook AI Manager Setup[/bold blue]")
    
    # Check environment variables
    console.print("\n[yellow]Checking configuration...[/yellow]")
    
    # Check email provider configuration
    console.print("\n[yellow]Checking email provider configuration...[/yellow]")
    
    try:
        settings.validate_email_config()
        console.print(f"[green]✓ Email provider configured: {settings.email_provider}[/green]")
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        console.print("\n[cyan]Email Provider Setup:[/cyan]")
        if settings.email_provider == "gmail":
            console.print("1. Go to https://console.cloud.google.com")
            console.print("2. Create project and enable Gmail API") 
            console.print("3. Download credentials.json file")
            console.print("4. Set GMAIL_ADDRESS in .env")
        else:
            console.print("1. Create Azure app registration")
            console.print("2. Set Microsoft Graph credentials in .env")
        return
    
    # Test email provider connection
    console.print(f"\n[yellow]Testing {settings.email_provider} connection...[/yellow]")
    email_interface = EmailInterface()
    
    if email_interface.test_connection():
        console.print(f"[green]✓ {settings.email_provider.title()} connection successful[/green]")
    else:
        console.print(f"[red]✗ {settings.email_provider.title()} connection failed[/red]")
        return
    
    # Test LLM configuration
    console.print("\n[yellow]Testing LLM configuration...[/yellow]")
    try:
        settings.validate_llm_config()
        classifier = EmailClassifier()
        provider_info = classifier.get_provider_info()
        
        console.print(f"[green]✓ LLM provider configured: {classifier.provider.name}[/green]")
        
        # Show available providers
        if provider_info['free_providers']:
            console.print(f"[cyan]Free providers available: {', '.join(provider_info['free_providers'])}[/cyan]")
        if provider_info['premium_providers']:
            console.print(f"[yellow]Premium providers available: {', '.join(provider_info['premium_providers'])}[/yellow]")
            
    except Exception as e:
        console.print(f"[red]✗ LLM configuration failed: {e}[/red]")
        console.print("\n[cyan]Free LLM Options:[/cyan]")
        console.print("1. [bold]Groq[/bold] (free tier, fast):")
        console.print("   - Get API key: https://console.groq.com")
        console.print("   - Add to .env: GROQ_API_KEY=your_key")
        console.print("   - Set: LLM_PROVIDER=groq")
        console.print("2. [bold]Google Gemini[/bold] (free tier):")
        console.print("   - Get API key: https://makersuite.google.com")
        console.print("   - Add to .env: GOOGLE_API_KEY=your_key")
        console.print("   - Set: LLM_PROVIDER=gemini")
        return
    
    console.print("\n[green]Setup complete! You're ready to start managing emails.[/green]")

@cli.command()
def stats():
    """Show email statistics"""
    console.print("[bold blue]Email Statistics[/bold blue]")
    
    fetcher = EmailInterface()
    
    with console.status("[bold green]Fetching email statistics..."):
        stats = fetcher.get_email_stats()
    
    table = Table(title="Email Folder Statistics")
    table.add_column("Folder", style="cyan")
    table.add_column("Total Emails", justify="right")
    table.add_column("Unread Emails", justify="right")
    
    for folder, data in stats.items():
        table.add_row(
            folder.title(),
            str(data['total_count']),
            str(data['unread_count'])
        )
    
    console.print(table)

@cli.command()
@click.option('--limit', default=50, help='Number of emails to analyze')
@click.option('--folder', default='inbox', help='Folder to analyze (inbox, junkemail, etc.)')
@click.option('--days', default=None, type=int, help='Only analyze emails from last N days')
@click.option('--save-results', is_flag=True, help='Save classification results to file')
@click.option('--provider', help='Specify LLM provider to use (groq, gemini, openai, anthropic)')
def analyze(limit: int, folder: str, days: Optional[int], save_results: bool, provider: Optional[str]):
    """Analyze emails and classify them"""
    console.print(f"[bold blue]Analyzing {limit} emails from {folder}[/bold blue]")
    
    # Initialize components
    fetcher = EmailInterface()
    classifier = EmailClassifier(provider) if provider else EmailClassifier()
    
    console.print(f"[dim]Using email provider: {fetcher.provider}[/dim]")
    console.print(f"[dim]Using LLM provider: {classifier.provider.name}[/dim]")
    
    # Fetch emails
    with console.status("[bold green]Fetching emails..."):
        emails = fetcher.fetch_emails(folder=folder, limit=limit, days_back=days)
    
    if not emails:
        console.print("[red]No emails found to analyze[/red]")
        return
    
    console.print(f"[green]Fetched {len(emails)} emails[/green]")
    
    # Classify emails
    results = []
    with Progress() as progress:
        task = progress.add_task("[green]Classifying emails...", total=len(emails))
        
        batch_size = settings.batch_size
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            batch_results = classifier.classify_emails_batch(batch, batch_size)
            results.extend(batch_results)
            progress.update(task, advance=len(batch))
    
    # Display results
    _display_classification_results(results)
    
    # Save results if requested
    if save_results:
        filename = f"classification_results_{folder}_{len(results)}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        console.print(f"[green]Results saved to {filename}[/green]")

@cli.command()
@click.option('--limit', default=100, help='Number of emails to process')
@click.option('--folder', default='inbox', help='Folder to clean (inbox, junkemail, etc.)')
@click.option('--days', default=None, type=int, help='Only process emails from last N days')
@click.option('--auto-delete', is_flag=True, help='Automatically delete emails classified as JUNK')
@click.option('--confidence-threshold', default=0.8, type=float, help='Minimum confidence for auto-actions')
@click.option('--provider', help='Specify LLM provider to use (groq, gemini, openai, anthropic)')
def clean(limit: int, folder: str, days: Optional[int], auto_delete: bool, confidence_threshold: float, provider: Optional[str]):
    """Clean up emails by classifying and organizing them"""
    console.print(f"[bold blue]Cleaning {limit} emails from {folder}[/bold blue]")
    
    if settings.dry_run:
        console.print("[yellow]Running in DRY RUN mode - no emails will be actually deleted[/yellow]")
    
    # Initialize components
    fetcher = EmailInterface()
    classifier = EmailClassifier(provider) if provider else EmailClassifier()
    actions = fetcher  # EmailInterface includes actions
    
    console.print(f"[dim]Using email provider: {fetcher.provider}[/dim]")
    console.print(f"[dim]Using LLM provider: {classifier.provider.name}[/dim]")
    
    # Fetch emails
    with console.status("[bold green]Fetching emails..."):
        emails = fetcher.fetch_emails(folder=folder, limit=limit, days_back=days)
    
    if not emails:
        console.print("[red]No emails found to clean[/red]")
        return
    
    console.print(f"[green]Fetched {len(emails)} emails[/green]")
    
    # Classify emails
    results = []
    with Progress() as progress:
        task = progress.add_task("[green]Classifying emails...", total=len(emails))
        
        batch_size = settings.batch_size
        for i in range(0, len(emails), batch_size):
            batch = emails[i:i + batch_size]
            batch_results = classifier.classify_emails_batch(batch, batch_size)
            results.extend(batch_results)
            progress.update(task, advance=len(batch))
    
    # Process results
    junk_emails = []
    high_confidence_junk = []
    
    for result in results:
        if result.get('category') == 'JUNK':
            junk_emails.append(result)
            if result.get('confidence', 0) >= confidence_threshold:
                high_confidence_junk.append(result)
    
    console.print(f"\n[yellow]Classification Summary:[/yellow]")
    console.print(f"Total JUNK emails found: {len(junk_emails)}")
    console.print(f"High confidence JUNK (≥{confidence_threshold}): {len(high_confidence_junk)}")
    
    # Auto-delete if requested
    if auto_delete and high_confidence_junk:
        if click.confirm(f"Delete {len(high_confidence_junk)} high-confidence junk emails?"):
            with Progress() as progress:
                task = progress.add_task("[red]Deleting emails...", total=len(high_confidence_junk))
                
                deleted_count = 0
                for result in high_confidence_junk:
                    email_id = result.get('email_id')
                    if email_id and actions.delete_email(email_id):
                        deleted_count += 1
                    progress.update(task, advance=1)
                
                console.print(f"[green]Successfully deleted {deleted_count} emails[/green]")
    
    # Display full results
    _display_classification_results(results)

@cli.command()
@click.option('--sender', help='Analyze specific sender')
@click.option('--limit', default=100, help='Number of emails to analyze for sender patterns')
def sender_analysis(sender: Optional[str], limit: int):
    """Analyze sender patterns to create classification rules"""
    console.print("[bold blue]Sender Analysis[/bold blue]")
    
    fetcher = EmailInterface()
    classifier = EmailClassifier()
    
    if sender:
        # Analyze specific sender
        with console.status(f"[bold green]Searching emails from {sender}..."):
            emails = fetcher.search_emails(f"from:{sender}", limit=limit)
        
        if not emails:
            console.print(f"[red]No emails found from {sender}[/red]")
            return
        
        subjects = [email.get('subject', '') for email in emails]
        analysis = classifier.analyze_sender(sender, subjects, len(emails))
        
        console.print(f"\n[bold]Analysis for {sender}:[/bold]")
        console.print(f"Category: {analysis.get('sender_category')}")
        console.print(f"Confidence: {analysis.get('confidence'):.2f}")
        console.print(f"Reasoning: {analysis.get('reasoning')}")
        console.print(f"Suggested Rule: {analysis.get('suggested_rule')}")
    
    else:
        console.print("[yellow]Please specify a sender with --sender flag[/yellow]")

@cli.command()
def llm_setup():
    """Help set up free LLM providers"""
    console.print("[bold blue]Free LLM Setup Guide[/bold blue]")
    
    console.print("\n[cyan]📚 Available Free Options:[/cyan]")
    
    # Check Groq
    console.print("\n[bold]1. Groq (Free Tier, Fast Inference)[/bold]")
    console.print("   [green]✓ Fast inference speed[/green]")
    console.print("   [green]✓ Good free tier limits[/green]")
    console.print("   [yellow]⚠ Requires API key[/yellow]")
    
    if settings.has_groq:
        console.print("   [green]✓ Groq API key configured[/green]")
    else:
        console.print("   [red]✗ Groq API key not configured[/red]")
        console.print("   [yellow]Setup steps:[/yellow]")
        console.print("   1. Visit: https://console.groq.com")
        console.print("   2. Create account and get API key")
        console.print("   3. Add to .env: [bold]GROQ_API_KEY=your_key_here[/bold]")
        console.print("   4. Set provider: [bold]LLM_PROVIDER=groq[/bold]")
    
    # Check Google Gemini
    console.print("\n[bold]2. Google Gemini (Free Tier)[/bold]")
    console.print("   [green]✓ High quality responses[/green]")
    console.print("   [green]✓ Generous free tier[/green]")
    console.print("   [yellow]⚠ Requires Google account[/yellow]")
    
    if settings.has_google:
        console.print("   [green]✓ Google API key configured[/green]")
    else:
        console.print("   [red]✗ Google API key not configured[/red]")
        console.print("   [yellow]Setup steps:[/yellow]")
        console.print("   1. Visit: https://makersuite.google.com/app/apikey")
        console.print("   2. Create API key")
        console.print("   3. Add to .env: [bold]GOOGLE_API_KEY=your_key_here[/bold]")
        console.print("   4. Set provider: [bold]LLM_PROVIDER=gemini[/bold]")
    
    # Current status
    console.print("\n[cyan]📊 Current Status:[/cyan]")
    available = settings.available_providers
    selected = settings.llm_provider
    
    if available:
        console.print(f"   Available providers: {', '.join(available)}")
        console.print(f"   Selected provider: [bold]{selected}[/bold]")
        
        if selected not in available:
            console.print(f"   [red]⚠ Selected provider '{selected}' is not available![/red]")
    else:
        console.print("   [red]No LLM providers configured[/red]")
    
    # Recommendations
    console.print("\n[cyan]💡 Recommendations:[/cyan]")
    console.print("   [bold]For speed & convenience:[/bold] Use Groq") 
    console.print("   [bold]For best quality:[/bold] Use Google Gemini")
    console.print("   [bold]For batch processing:[/bold] Use Gemini (better batch support)")
    
    if not available:
        console.print("\n[yellow]⚡ Quick Start:[/yellow]")
        console.print("   [bold]Easiest:[/bold] Get Groq API key (2 minutes)")
        console.print("   [bold]Best quality:[/bold] Get Google Gemini API key (2 minutes)")

@cli.command()
def providers():
    """List available LLM providers and their status"""
    console.print("[bold blue]LLM Provider Status[/bold blue]")
    
    try:
        classifier = EmailClassifier()
        provider_info = classifier.get_provider_info()
        
        table = Table(title="LLM Providers")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Type", style="dim")
        table.add_column("Notes")
        
        # Check each provider
        providers_data = [
            ("groq", "API (Free Tier)", "Fast inference, good free limits"),
            ("gemini", "API (Free Tier)", "Google's model, generous limits, good batch support"),
            ("openai", "API (Paid)", "GPT models, requires payment"),
            ("anthropic", "API (Paid)", "Claude models, requires payment")
        ]
        
        for provider, type_info, notes in providers_data:
            if provider in provider_info['available_providers']:
                if provider == provider_info['current_provider']:
                    status = "🎯 Active"
                else:
                    status = "✅ Available"
            else:
                status = "❌ Not Available"
            
            table.add_row(provider.title(), status, type_info, notes)
        
        console.print(table)
        
        if provider_info['current_provider']:
            console.print(f"\n[green]Currently using: {provider_info['current_provider']}[/green]")
            console.print(f"Selected in settings: {provider_info['selected_provider']}")
        else:
            console.print("\n[red]No provider currently active[/red]")
            
    except Exception as e:
        console.print(f"[red]Error checking providers: {e}[/red]")

def _display_classification_results(results: List[Dict[str, Any]]):
    """Display classification results in a nice table"""
    
    # Count by category
    category_counts = {}
    for result in results:
        category = result.get('category', 'UNKNOWN')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Summary table
    summary_table = Table(title="Classification Summary")
    summary_table.add_column("Category", style="cyan")
    summary_table.add_column("Count", justify="right")
    summary_table.add_column("Percentage", justify="right")
    
    total = len(results)
    for category, count in category_counts.items():
        percentage = (count / total * 100) if total > 0 else 0
        summary_table.add_row(category, str(count), f"{percentage:.1f}%")
    
    console.print(summary_table)
    
    # Show sample high-confidence classifications
    high_confidence = [r for r in results if r.get('confidence', 0) >= 0.8]
    if high_confidence:
        console.print(f"\n[bold]Sample High-Confidence Classifications (showing first 10):[/bold]")
        
        detail_table = Table()
        detail_table.add_column("Category", style="cyan")
        detail_table.add_column("Confidence", justify="right")
        detail_table.add_column("Reason", style="dim")
        
        for i, result in enumerate(high_confidence[:10]):  # Show first 10
            detail_table.add_row(
                result.get('category', 'UNKNOWN'),
                f"{result.get('confidence', 0):.2f}",
                result.get('reason', 'No reason provided')[:60] + "..."
            )
        
        console.print(detail_table)

if __name__ == "__main__":
    cli()