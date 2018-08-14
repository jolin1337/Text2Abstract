import re


body_pattern = re.compile(r'<([^p\/]).*?>.*?<\/\1.*?>')
html_pattern = re.compile(r'<.*?>')
meta_pattern = re.compile(r'\[.*?\]')
dspaces_pattern = re.compile(r' +')
def striphtml(data):
  body_cleared = body_pattern.sub(' ', data)
  html_cleared = html_pattern.sub(' ', body_cleared)
  meta_cleared = meta_pattern.sub(' ', html_cleared)
  dspaces_cleared = dspaces_pattern.sub(' ', meta_cleared)
  return dspaces_cleared


