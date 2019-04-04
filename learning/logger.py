from learning import config


def log(*text):
  if config.verbose:
    print(*text)
