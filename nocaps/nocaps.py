from rich.console import Console
def thinking_animation(stop_loading):
  from rich.panel import Panel
  from rich.live import Live
  from time import sleep
  console = Console()

  message_base = 'Let me help you with this'
  i = 0
  panel = Panel(message_base, border_style='cyan')
  with Live(panel, refresh_per_second=4, transient=True) as live:
    while not stop_loading.is_set():
      dots = '.' * (i % 4)
      panel = Panel(f'{message_base}{dots}', border_style='cyan')
      live.update(panel)
      sleep(0.5)
      i += 1

def main():
  import os
  import threading
  import google.generativeai as genai
  from argparse import ArgumentParser, Namespace
  from subprocess import run, CalledProcessError
  from rich import print

  # imports configuration
  parser = ArgumentParser()
  console = Console()
  genai.configure(api_key=api_key)
  model=genai.GenerativeModel("gemini-2.0-flash")
  parser.usage = "Learn python better!!"

  # cli configuration
  parser.add_argument('filepath', help='Add the path to the file')
  parser.add_argument('-v', '--verbose', action='count', help='Adds verbose to output')
  args: Namespace = parser.parse_args()


  try:

    # checking if the the file runs
    with open(args.filepath, 'r', encoding='utf-8') as f:
      file_content = f.read()
    file_extention = args.filepath.split('.')[-1]

    match file_extention:
      case 'py':
        result = run(['python', args.filepath], capture_output=True, text=True, check=True)
      case 'js':
        result = run(['node', args.filepath], capture_output=True, text=True, check=True)
      case 'java':
        # Compile the Java file first
        compile_result = run(['javac', args.filepath], capture_output=True, text=True)
        class_name = args.filepath.split('.')[-2].replace('\\', '').replace('/', '')
        result = run(['java', class_name], capture_output=True, text=True, check=True)
      case _:
        stop_loading.set()
        thread.join()
        print(f"[yellow]File extension '.{file_extention}' is not supported.[/yellow]")
        return

    print(f"{result.stdout}")

  # debugging using gemini-2.0-flash
  except CalledProcessError as e:

    # starting the loading animation thread
    stop_loading = threading.Event()
    thread = threading.Thread(target=thinking_animation, args=(stop_loading,))
    thread.start()

    # prompting ai for response
    error = e.stderr
    file_text = file_content

    roast_prompt = f"""
      Analyze the following code written by a human developer. 
      Identify areas of inefficiency, poor style, potential bugs, 
      security vulnerabilities (if applicable), or just plain head-scratching choices. 
      Provide a concise, witty, and extremely insulting roast targeting these 
      specific issues within 12 words. Give only the roast for the output.

      ---

      {file_text}

      ---

      Example Roast Output:

      My Grandmother runs faster than your code.

      I've seen spaghetti with fewer tangles than your function calls.

      Your code runs like a drunk grandma on rollerblades — in reverse.

      I debugged it… turns out the real bug was you.
      """
    prompt = f"""{file_text}\n The above file is resulting in this error: {error} \nSuggest a fix, formatting the response in four paragraphs following this format:

      :thumbs_down: : 
      [red] [Indicate the *wrong* code snippet (if applicable)] [/red]
        
      [yellow] [Provide a breif explanation of the fix] [/yellow]

      :thumbs_up: : 
      [green] [Indicate the correct(the fix) code snippet (if applicable)] [/green]
        
      [cyan] [Suggest any short further enhancements or best practices under 30 words] [/cyan]
      """
    roast = model.generate_content(roast_prompt)
    prompt_response = model.generate_content(prompt)
    response = prompt_response.text.replace('```python\n', '')
    response = response.replace('\n```', '')

    # stopping the loading animation
    stop_loading.set()
    thread.join()
    console.clear_live()  # Clear console after animation

    print(f"\n[blue]{roast.text.strip()}[/blue]\n\nBut here's what you can do about it\n")
    print(response.strip() + "\n")
if __name__ == "__main__":
  main()