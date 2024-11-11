from os import path, listdir, mkdir, rmdir, rename
from typing import Any
import json
import re

## Paths
this_path: str = path.dirname(path.realpath(__file__))
sort_path: str = path.join(path.expanduser("~"), "Downloads")

## Funções
# Pegar um dicionário de um json
def json_to_dict(file_path: str) -> dict:
  with open(file_path, 'r', encoding='utf8') as json_file:
    return json.load(json_file)

# Pegar a chave por um valor em um dicionário
def get_dict_key(dict: dict, value_to_get: Any) -> Any:
  key: list = [key for key,value in dict.items() if value == value_to_get]
  return key[0]

# Seleciona em qual folder o arquivo ten que ir dependendo da extensão dele
def correct_folder(json_dict: dict, file_ext: str, file_types: dict) -> str:
  for folder in json_dict["folders"].values():
    if folder != "Others":
      if file_ext.lower() in file_types[folder]:
        return folder

  return "Others"

# Se o arquivo existir, o novo nome dele vai ter um (num) no final
def dont_overwrite(file_name: str, file_ext: str) -> str:
  pattern: str = "^(0?[0-9]|[1-9][0-9])$"
  if re.search(pattern, file_name):
    found: list = re.findall(pattern, file_name)[0]
    number: int = int("".join([s for s in found if s.isdigit()])) + 1
    return re.sub(pattern, f"({number})", file_name) + file_ext
  return f"{file_name} (1){file_ext}"

def main() -> None:
  ## Definindo variáveis
  file_types: dict = json_to_dict(path.join(this_path, "file_types.json"))
  preset: dict = json_to_dict(path.join(this_path, "preset.json"))
  p_folders: dict = preset["folders"]
  files: list = listdir(sort_path)
  move_to: dict = {}
  destination: str = ""

  ## Associar nomes das pastas aos tipos
  for file in files:
    if file not in preset["ignore"]:
      if file not in p_folders:
        if path.isfile(path.join(sort_path, file)):
          extension: str = path.splitext(file)[-1]
          folder_to_go: str = correct_folder(preset, extension, file_types)
          destination: str = path.join(sort_path, get_dict_key(p_folders, folder_to_go), file)
        else:
          if file not in p_folders.keys():
            destination: str = path.join(sort_path, get_dict_key(p_folders, "Others"), file)
        while path.exists(destination):
          destination: str = path.join(path.dirname(destination), dont_overwrite(*path.splitext(destination)))
        move_to[file] = destination

  # Mover os arquivos (e criar as pastas caso elas não existam)
  for file in move_to:
    prev_path: str = path.join(sort_path, file)
    next_path: str = move_to[file]
    parent_dir: str = path.dirname(move_to[file])
    if not path.exists(parent_dir):
      mkdir(parent_dir)
    rename(prev_path, next_path)

  # Excluir as pastas que não tem nenhum arquivo dentro
  for folder in p_folders:
    folder_path: str = path.join(sort_path, folder)
    if path.exists(folder_path):
      if listdir(folder_path) == []:
        rmdir(folder_path)

if __name__ == "__main__":
  main()
