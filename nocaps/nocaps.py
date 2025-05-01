def main():
  from argparse import ArgumentParser, Namespace
  from subprocess import run, CalledProcessError
  import google.generativeai as genai
  from rich import print

  parser = ArgumentParser()
  api_key = 'AIzaSyDSY4o5XOJiPddVh30qs_NuilmYNT-WUOs'
  genai.configure(api_key=api_key)
  model=genai.GenerativeModel("gemini-2.0-flash")

  parser.usage = "Learn python better!!"

  parser.add_argument('filepath', help='Add the path to the file')
  parser.add_argument('-v', '--verbose', action='count', help='Adds verbose to output')

  args: Namespace = parser.parse_args()

  try:
    file_content = run(f'type "{args.filepath}"', capture_output=True, text=True, check=True, shell=True)
    result = run(['python', args.filepath], capture_output=True, text=True, check=True, shell=True)
    print(f"{result.stdout}")
  except CalledProcessError as e:
    error = e.stderr
    file_text = file_content.stdout

    roast_prompt = f"""
      Analyze the following Python code written by a human developer. Identify areas of inefficiency, poor style, potential bugs, security vulnerabilities (if applicable), or just plain head-scratching choices. Provide a concise, witty, and extremely insulting roast targeting these specific issues within 20 words. Give only the roast for the output.

  ---

  {file_text}

  ---

  Example Roast Output:

  My Grandmother runs faster than your code.

  This function's error handling strategy seems to be "hope for the best."

  I've seen spaghetti with fewer tangles than your function calls.

  Your code runs like a drunk grandma on rollerblades — in reverse.

  I debugged it… turns out the real bug was you.

  I've seen malware more organized than this mess.
  """

    prompt = f"""{file_text}\n The above file is resulting in this error: {error} \nSuggest a fix, formatting the response in four paragraphs following this format:

  Indicate the *wrong* code snippet (if applicable) by enclosing it in '[red]' and '[/red]'.
    
  Provide a *breif explanation* of the fix by enclosing it in '[yellow]' and '[/yellow]'.

  Indicate the *correct* code snippet (the fix) by enclosing it in '[green]' and '[/green]'.
    
  Suggest any *short further enhancements* or best practices under 30 words by enclosing them in '[cyan]' and '[/cyan]'.

  You can use multiple paragraphs if needed to clearly separate these sections."""
    roast = model.generate_content(roast_prompt)
    prompt_response = model.generate_content(prompt)
    response = prompt_response.text.replace('```python\n', '')
    response = response.replace('\n```', '')

    print(f"\n[red]{roast.text}[/red]\n[cyan]But here's what you can do about it![/cyan]\n")
    print(response)
if __name__ == "__main__":
  main()