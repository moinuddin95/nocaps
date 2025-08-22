from rich.console import Console
import threading
def thinking_animation(stop_loading):
  from rich.panel import Panel
  from rich.live import Live
  from time import sleep

  message_base = 'Let me help you with this'
  i = 0
  panel = Panel(message_base, border_style='cyan')
  with Live(panel, refresh_per_second=4, transient=True) as live:
    while stop_loading.is_set() == False:
      dots = '.' * (i % 4)
      panel = Panel(f'{message_base}{dots}', border_style='cyan')
      live.update(panel)
      sleep(0.5)
      i += 1

stop_loading = threading.Event()
thread = None
console = Console()

def start_animation():
  global thread
  stop_loading.clear()
  thread = threading.Thread(target=thinking_animation, args=(stop_loading,))
  thread.start()

def stop_animation():
  global thread
  stop_loading.set()
  if thread is not None:
    thread.join()
    thread = None
  # Clear console after animation
  console.clear_live()

def prompt_the_api(prompt):
  import requests
  from authorization import load_tokens, refresh_access_token, device_authorization
  
  access_token, refresh_token = load_tokens()

  if not access_token or not refresh_token:
    stop_animation()
    device_authorization()
  
  def poll_request():
    access_token = load_tokens()[0]
    response = requests.post(
      "http://localhost:3000/debug",
      json={"prompt": prompt},
      headers={"Authorization": f"Bearer {access_token}"}
    )
    return response

  try:
    data = poll_request().json()
  except Exception:
    refresh_access_token(refresh_token)
    try:
      data = poll_request().json()
    except Exception:
      stop_animation()
      raise Exception("Failed to parse response from API")

  if 'output' in data:
    return data['output']
  else:
    stop_animation()
    if 'error' in data:
      raise Exception(data['error'])
    else:
      raise Exception("Unexpected response format from API")

def handle_error(e, file_content):
  start_animation()

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
  roast = prompt_the_api(roast_prompt)
  prompt_response = prompt_the_api(prompt)
  response = prompt_response.replace('```python\n', '')
  response = response.replace('\n```', '')

  stop_animation()

  print(f"\n[blue]{roast.strip()}[/blue]\n\nBut here's what you can do about it\n")
  print(response.strip() + "\n")

def main():
  from argparse import ArgumentParser, Namespace
  from subprocess import run, CalledProcessError
  from rich import print

  # imports configuration
  parser = ArgumentParser()

  parser.usage = "Learn python better!!"

  # cli configuration
  parser.add_argument('filepath', help='Add the path to the file')
  parser.add_argument('-v', '--verbose', action='count', help='Adds verbose to output')
  args: Namespace = parser.parse_args()

  try:
    try:
      # checking if the the file runs
      with open(args.filepath, 'r', encoding='utf-8') as f:
        file_content = f.read()
    except Exception:
      print("[yellow]File is not found or supported.[/yellow]")
      return

    file_extention = args.filepath.split('.')[-1]
    #checking if the file is compatible
    match file_extention:
      case 'py':
        result = run(['python', args.filepath], capture_output=True, text=True, check=True)
      case 'js':
        result = run(['node', args.filepath], capture_output=True, text=True, check=True)
      case 'java':
        # Compile the Java file first
        run(['javac', args.filepath], capture_output=True, text=True)
        class_name = args.filepath.split('.')[-2].replace('\\', '').replace('/', '')
        result = run(['java', class_name], capture_output=True, text=True, check=True)
      case _:
        # If the file extension is not supported
        print(f"[yellow]File extension '.{file_extention}' is not supported.[/yellow]")
        return

    # print the output if there are not errors
    print(f"{result.stdout}")

  # debugging using the api
  except CalledProcessError as e:
    handle_error(e, file_content)
if __name__ == "__main__":
  main()