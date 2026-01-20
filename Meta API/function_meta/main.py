import json
import pandas as pd
from pandas.io import gbq
import os
from datetime import datetime, timedelta
from pytz import timezone
from controller.MetaController import MetaController
from database.BigQuery import BigQuery
import logging as log
from SecretManager import SecretManager



def get_parameter(json, parametro):
    valor = json[parametro]
    if valor == None:
        raise Exception(f"O parâmetro {parametro} precisa ser preenchido.")
    return valor 

def main(request):
    
    log.info("Iniciando execução Meta")
    
    secret_manager = SecretManager()

    secret_id = "{INSIRA O NOME DO SECRET}"
    project_id = "76816773014" # PROJECT_ID DO PROJETO CADMETRICS-PRD
    version_id = "latest" #SEMPRE LATEST

    secret = secret_manager.access_secret_version(
        secret_id=secret_id,
        project_id=project_id,
        version_id=version_id
    )

    secret = json.loads(secret)
    access_token = secret["access_token"]
    app_id = secret["app_id"]
    app_key_secret = secret["app_secret"]
  
    request_json = request.get_json()
   
    rst = None

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(base_dir, 'config', 'credentials.json')

    try:
        with open(config_file_path, 'r') as f:
            credentials = json.load(f)

        certificate_big_query = credentials.get('certificate_big_query')

    except:
        print(f"ERRO: Arquivo de configuração não encontrado em: {config_file_path}")
        certificate_big_query = None
   
    days_reprocess = 7
   
    
    # parametros
    project_id = get_parameter(request_json, 'project_id')
    destination_table = get_parameter(request_json, 'destination_table')
    if_exists = get_parameter(request_json, 'if_exists')
    
    account_list= get_parameter(request_json, 'account_list')
    fields_list= get_parameter(request_json, 'fields_list')

   

    if (request_json["start_date"] == "" or  request_json["end_date"] == ""):  
        start_date_tmp = datetime.now() - timedelta(days=days_reprocess)
        end_date_tmp = datetime.now() - timedelta(days=0)
        start_date = start_date_tmp.strftime("%Y-%m-%d")
        end_date = end_date_tmp.strftime("%Y-%m-%d")
    else:
        start_date = request_json["start_date"]
        end_date = request_json["end_date"]

    log.info(f"Project_id: {request_json['project_id']}")
    log.info(f"Project_id get_parameter: {project_id}")
    log.info(f"All JSON: {request_json}")
    
    
    for account_id in account_list:
    
        
        # Cria uma instância de MetaController
        meta_api = MetaController(access_token, app_id, app_key_secret, account_id, fields_list, start_date, end_date)

        # Autentica a instância
        meta_api.auth()
            
        # Chama o método request_report com as datas e dataframe apropriados
        df = meta_api.request_report('df')

        # Function to extract the 'value' from each dictionary
        def extract_value(dictionary_list):
            if isinstance(dictionary_list, list) and len(dictionary_list) > 0:
                dictionary = dictionary_list[0]
                return dictionary.get('value', None)
            else:
                return None

        for col in ['video_play_actions', 'video_thruplay_watched_actions', 'video_p100_watched_actions', 'video_p25_watched_actions']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: extract_value(x))
            else:
                log.warning(f"Coluna {col} não encontrada no DataFrame. Pulando.")


        #instancia classe responsável pela comunicação com BigQuery
        bq = BigQuery(certificate_big_query, project_id)

        # ## efetua autenticação com BigQuery
        bq.auth()

       # exporta os dados para o BigQuery
       #A conta ´pode não ter dados para o periodo, retornando um df vazio
        if df is not None: 
            rstLinesLoading = bq.export(df, start_date, end_date, destination_table, project_id, if_exists, account_id)

            rst = {
                "status": "Ok",
                "message": "Data Loaded",
                "lines": rstLinesLoading
            }
        else:
            rst = {
                "status": "Ok",
                "message": "No data to load into bigquery",
                "lines": 0
            }


    return json.dumps(rst), 200, {'Content-Type': 'application/json'}

