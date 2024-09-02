import os, shutil, json, re
from os import path
# from typing import *

## Paths
this_path = path.dirname(path.realpath(__file__)) 
sort_path = path.join(path.expanduser("~"), "Downloads")

## Funções
# Pegar um dicionário de um json
def json_to_dict(file_path: str) -> dict:
  with open(file_path, 'r', encoding='utf8') as json_file:
    return json.load(json_file)

# Pegar a chave por um valor em um dicionário
def get_dict_key(dict: dict, value_to_get: any) -> any:
  key = [key for key,value in dict.items() if value == value_to_get]
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
  pattern = "^(0?[0-9]|[1-9][0-9])$"
  # for pattern in ["\([0-9]\)$", "\([1-9][0-9]\)$"]:
  if re.search(pattern, file_name):
    found = re.findall(pattern, file_name)[0]
    number = int("".join([s for s in found if s.isdigit()])) + 1
    return re.sub(pattern, f"({number})", file_name) + file_ext
  
  return f"{file_name} (1){file_ext}"

def main():
  ## Definindo variáveis
  file_types: dict = json_to_dict(path.join(this_path, "file_types.json"))
  preset = json_to_dict(path.join(this_path, "preset.json"))
  p_folders = preset["folders"]
  files = os.listdir(sort_path)
  move_to = {}
  destination = ""
  
  ## Associar nomes das pastas aos tipos
  for file in files:
    if file not in preset["ignore"]:
      if file not in p_folders:
        if path.isfile(path.join(sort_path, file)):
          name, extension = path.splitext(file)
          folder_to_go = correct_folder(preset, extension, file_types)
          destination = path.join(sort_path, get_dict_key(p_folders, folder_to_go), file)
        else:
          if file not in p_folders.keys():
            destination = path.join(sort_path, get_dict_key(p_folders, "Others"), file)
        while path.exists(destination):
          new_name, extension = path.splitext(destination)
          destination = path.join(path.dirname(destination), dont_overwrite(new_name, extension))
        move_to[file] = destination
  
  
  # Mover os arquivos (e criar as pastas caso elas não existam)
  for file in move_to:
    prev_path = path.join(sort_path, file)
    next_path = move_to[file]
    parent_dir = path.dirname(move_to[file])
    if not path.exists(parent_dir):
      os.mkdir(parent_dir)
    shutil.move(prev_path, next_path)
  
  
  # Excluir as pastas que não tem nenhum arquivo dentro
  for folder in p_folders:
    folder_path = path.join(sort_path, folder)
    if path.exists(folder_path):
      if os.listdir(folder_path) == []:
        os.rmdir(folder_path)

if __name__ == "__main__":
  main()
