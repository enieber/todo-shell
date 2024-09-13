import os
import subprocess
import hashlib
import requests
import click
from datetime import datetime, timedelta
from colorama import Fore
import pyfiglet
import json


# Definições de variáveis
tname = datetime.now().strftime("%d%m%y.md")
folder = os.path.join(os.getenv("HOME"), "workspace/pop/tasks")
tfile = os.path.join(folder, tname)
cityCode = 4704

# Funções

def remove_task(task_id):
    if not task_id:
        print("Erro: você precisa fornecer um ID para alterar")
    else:
        print(f"Removendo tarefa {task_id}")
        deleted_file = f"/tmp/removed-{task_id}-task.md"
        with open(tfile, "r") as f_in, open(deleted_file, "w") as f_out:
            for line in f_in:
                if not f"{task_id} -" in line:
                    f_out.write(line)
        os.remove(tfile)
        os.rename(deleted_file, tfile)
        subprocess.run(["glow", tfile])

def update_state(task_id, state):
    if not task_id:
        print("Erro: você precisa fornecer um ID para alterar")
    elif state is None:
        print("Erro: você precisa fornecer um status para alterar")
    else:
        filter_todo = f"- [ ] {task_id} - "
        checked_todo = f"- [x] {task_id} - " if state else f"- [ ] {task_id} - "
        with open(tfile, "r") as f_in, open("/tmp/file.md", "w") as f_out:
            for line in f_in:
                f_out.write(line.replace(filter_todo if not state else checked_todo, checked_todo))
        os.remove(tfile)
        os.rename("/tmp/file.md", tfile)
        subprocess.run(["glow", tfile])

def parse_clima(path_json):
    # Abrir e carregar o conteúdo do arquivo JSON
    with open(path_json, "r") as f:
        data = json.load(f)  # Parseia o JSON

    # Extraindo as informações necessárias do JSON
    cidade = data.get("cidade", "Cidade não encontrada")
    clima = data.get("clima", [{}])[0]  # Obtém o primeiro elemento da lista "clima"
    min_temp = clima.get("min", "N/A")
    max_temp = clima.get("max", "N/A")
    cond = clima.get("condicao_desc", "Condição não encontrada")

    # Formatação da data e dia da semana
    dt = datetime.now().strftime("%d/%m/%y")
    dweek = datetime.now().strftime("%A")

    # Retornando o resultado formatado
    return f"# Diário - {dt}\n\n- {dweek} - {cidade} - max: {max_temp} ºC min: {min_temp} ºC \n- Condições: {cond}\n\n## TODO\n\n"


def new_day():
    path_json = "/tmp/clima.json"
    url = f"https://brasilapi.com.br/api/cptec/v1/clima/previsao/{cityCode}"
    response = requests.get(url)
    with open(path_json, "w") as f:
        f.write(response.text)
    clima_text = parse_clima(path_json)
    with open(tfile, "w") as f:
        f.write(clima_text)
    subprocess.run(["glow", tfile])

def print_name():
    styled_text=pyfiglet.figlet_format('Today CLI',font= 'doom')
    print(Fore.WHITE + styled_text)
    print(datetime.now().strftime("%H:%M"))

# Usando a biblioteca click
@click.group()
def cli():
    """CLI para gerenciamento de tarefas diárias."""
    pass

@cli.command()
def new():
    """Cria um novo arquivo de tarefas para o dia."""
    new_day()

@cli.command()
@click.argument('task_id')
def delete(task_id):
    """Remove uma tarefa pelo ID."""
    remove_task(task_id)

@cli.command()
@click.argument('task_desc')
def add(task_desc):
    """Adiciona uma nova tarefa."""
    hash_id = hashlib.sha512(task_desc.encode()).hexdigest()[:4]
    with open(tfile, "a") as f:
        f.write(f" - [ ] {hash_id} - {task_desc}\n")
    print(f"Tarefa adicionada com ID: {hash_id}")

@cli.command()
@click.argument('task_id')
def done(task_id):
    """Marca uma tarefa como concluída pelo ID."""
    print(f"Finalizando item - {task_id}")
    update_state(task_id, True)

@cli.command()
@click.argument('task_id')
def undone(task_id):
    """Marca uma tarefa como não concluída pelo ID."""
    print(f"Marcando como não feito o item - {task_id}")
    update_state(task_id, False)

@cli.command()
def show():
    """Exibe as tarefas e o horário atual."""
    print_name()
    subprocess.run(["glow", tfile])

@cli.command()
def short():
    """Exibe as tarefas e o horário atual."""
    print_name()
    subprocess.run(["glow", tfile])

@cli.command()
@click.argument('days_back', type=int)
def day(days_back):
    """Mostra o arquivo de tarefas de dias anteriores."""
    file_result = (datetime.now() - timedelta(days=days_back)).strftime("%d%m%y.md")
    res = os.path.join(folder, file_result)
    subprocess.run(["glow", res])    

@cli.command()
def edit():
    """Abre o arquivo de tarefas do dia para edição."""
    subprocess.run(["nvim", tfile])

# Função principal
if __name__ == '__main__':
    cli()
