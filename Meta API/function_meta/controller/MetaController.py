import pandas as pd
from pandas import DataFrame
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from requests import get
from json import load
import json
import requests

DEFAULT_TIMEOUT = 12   # segundos
CHUNK_SIZE = 200       # quantos ids processar por chunk (ajuste se necessário)

class MetaController:
    
    def __init__(self, access_token, app_id, app_key_secret, account_id, fields_list, start_date, end_date):
        self.access_token = access_token
        self.app_id = app_id
        self.app_key_secret = app_key_secret
        self.account_id = account_id
        self.fields_list = fields_list
        self.start_date = start_date
        self.end_date = end_date

    def auth(self):
        params = {
            'access_token': self.access_token,
            'fields': self.fields_list,
            'breakdown': 'publisher_platform',
            'level': 'ad',
            'time_range': f'{{"since": "{self.start_date}", "until": "{self.end_date}"}}',
            'time_increment': 1,
            'status': ['active', 'paused', 'archived']
        }

        url = f'https://graph.facebook.com/v24.0/act_{self.account_id}/insights'
        response = get(url, params)
        if response.status_code == 200:
            print("Autenticação bem sucedida!")
        else:
            print("Autenticação falhou!")
            raise Exception("Autenticação Falhou: " + response.text)
                    
    def is_auth(self):
        return self.auth()
    
    def request_report(self, df):   
        params = {
            'access_token': self.access_token,
            'fields': self.fields_list,
            'breakdown': 'publisher_platform',
            'level': 'ad',
            'time_range': f'{{"since": "{self.start_date}", "until": "{self.end_date}"}}',
            'time_increment': 1,
            'status': ['active', 'paused', 'deleted', 'archived'],
        }
        
        responses = []
        url = f'https://graph.facebook.com/v24.0/act_{self.account_id}/insights'
        response = get(url, params)
        
        if response.status_code == 200:
            response_json = response.json()
            if 'data' in response_json and response_json['data']:
                responses.append(response_json)
                print("Dados encontrados para a conta: " + str(self.account_id))
                
                while 'paging' in response_json and 'cursors' in response_json['paging']:
                    after_cursor = response_json['paging']['cursors'].get('after')
                    
                    if after_cursor:
                        params['after'] = after_cursor
                        response = get(url, params)
                        print('Paginando dados para a conta: ' + str(self.account_id))
                        
                        if response.status_code == 200:
                            response_json = response.json()
                            responses.append(response_json)
                            print("Dados encontrados para a conta: " + str(self.account_id))
                        else:
                            print(response.json())
                            raise Exception("Erro ao buscar dados da conta: " + str(self.account_id))
                    else:
                        print("Não há mais páginas para recuperar.")
                        break
            else:
                print('Sem dados para a conta: ' + str(self.account_id))
        else:
            print(response.json())
            raise Exception("Erro ao buscar dados da conta: " + str(self.account_id))
            
        # Extrair apenas os valores de dados de cada resposta
        data_values = [data for response in responses if 'data' in response for data in response['data']]
        
        # Criar o DataFrame com os valores dos dados
        self.df = DataFrame(data_values)
      
        # Adicionar colunas adicionais e renomear colunas
        self.df.insert(0, 'media_source', 'Meta')
        self.df['date_loading'] = datetime.now()
        self.df.rename(columns={'date_start': 'date_reference'}, inplace=True)
        
        return self.df

    def get_image_assets_batch(self, df):
        """
        Usa /act_<account_id>/insights?breakdowns=image_asset para extrair image_asset.image_url (FORMATO 1).
        Retorna o DataFrame com coluna 'ad_image_hd' preenchida quando existir.
        Rápido porque processa em chunks e usa filtering para limitar por ad_id.
        """
        if "ad_id" not in df.columns or df.empty:
            df["ad_image_hd"] = None
            return df

        ad_ids = df["ad_id"].dropna().astype(str).unique().tolist()
        ad_image_map = {}

        for i in range(0, len(ad_ids), CHUNK_SIZE):
            chunk = ad_ids[i:i + CHUNK_SIZE]
            url = f"https://graph.facebook.com/v24.0/act_{self.account_id}/insights"
            params = {
                "access_token": self.access_token,
                "level": "ad",
                "breakdowns": "image_asset",
                "fields": "ad_id",
                "time_range": f'{{"since":"{self.start_date}","until":"{self.end_date}"}}',
                "limit": 1000
            }
            filtering = [{"field": "ad.id", "operator": "IN", "value": chunk}]
            params["filtering"] = json.dumps(filtering)

            try:
                r = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
                if r.status_code != 200:
                    print(f"[image_asset] status {r.status_code}: {r.text}")
                    continue
                js = r.json()
                for rec in js.get("data", []):
                    ad = str(rec.get("ad_id"))
                    ia = rec.get("image_asset")
                    chosen = None
                    # FORMATO 1: lista de dicts com 'image_url' ou 'url'
                    if isinstance(ia, list):
                        for item in ia:
                            if item.get("image_url"):
                                chosen = item.get("image_url")
                                break
                            if item.get("url"):
                                chosen = item.get("url")
                                break
                    elif isinstance(ia, dict):
                        chosen = ia.get("image_url") or ia.get("url")
                    if ad and chosen:
                        ad_image_map[ad] = chosen

                # paginação básica dentro do chunk (next link)
                next_url = js.get("paging", {}).get("next")
                while next_url:
                    r2 = requests.get(next_url, timeout=DEFAULT_TIMEOUT)
                    if r2.status_code != 200:
                        break
                    js2 = r2.json()
                    for rec in js2.get("data", []):
                        ad = str(rec.get("ad_id"))
                        ia = rec.get("image_asset")
                        chosen = None
                        if isinstance(ia, list):
                            for item in ia:
                                if item.get("image_url"):
                                    chosen = item.get("image_url")
                                    break
                                if item.get("url"):
                                    chosen = item.get("url")
                                    break
                        elif isinstance(ia, dict):
                            chosen = ia.get("image_url") or ia.get("url")
                        if ad and chosen:
                            ad_image_map[ad] = chosen
                    next_url = js2.get("paging", {}).get("next")

            except Exception as e:
                print(f"Erro ao obter image_asset chunk: {e}")
                continue

        # preencher coluna de forma vetorizada (map)
        df["ad_image_hd"] = df["ad_id"].astype(str).map(ad_image_map)
        return df

    # ---------- B) Fallback: buscar via creatives (assets / child_attachments / video thumbnails) ----------
    def get_hd_from_creatives_batch(self, df):
        """
        Fallback quando não existir image_asset:
        - converte ad_id -> creative_id (batch)
        - consulta creatives em batch pedindo assets/asset_feed_spec/object_story_spec
        - extrai a melhor image_url possível
        """
        if "ad_id" not in df.columns or df.empty:
            df["ad_image_hd"] = None
            return df

        ad_ids = df["ad_id"].dropna().astype(str).unique().tolist()
        ad_to_creative = {}

        # 1) ad -> creative (batch)
        for i in range(0, len(ad_ids), CHUNK_SIZE):
            chunk = ad_ids[i:i + CHUNK_SIZE]
            ids_param = ",".join(chunk)
            url = "https://graph.facebook.com/v24.0/"
            params = {"ids": ids_param, "fields": "creative", "access_token": self.access_token}
            try:
                r = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
                if r.status_code != 200:
                    print("Erro batch ad->creative:", r.status_code, r.text)
                    continue
                js = r.json()
                for ad, content in js.items():
                    cid = (content.get("creative") or {}).get("id")
                    if cid:
                        ad_to_creative[str(ad)] = str(cid)
            except Exception as e:
                print("Erro no batch ad->creative:", e)
                continue

        if not ad_to_creative:
            df["ad_image_hd"] = None
            return df

        # 2) creative -> obter melhores imagens (batch)
        creative_ids = list(set(ad_to_creative.values()))
        creative_image_map = {}
        for i in range(0, len(creative_ids), CHUNK_SIZE):
            chunk = creative_ids[i:i + CHUNK_SIZE]
            ids_param = ",".join(chunk)
            url = "https://graph.facebook.com/v24.0/"
            params = {
                "ids": ids_param,
                "fields": "object_story_spec,image_url,thumbnail_url,asset_feed_spec",
                "access_token": self.access_token
            }
            try:
                r = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
                if r.status_code != 200:
                    print("Erro batch creatives:", r.status_code, r.text)
                    continue

                js = r.json()

                for cid, content in js.items():
                    best = None

                    # 1️⃣ asset_feed_spec.images (IMAGENS HD DE ESTÁTICOS)
                    afs = content.get("asset_feed_spec") or {}
                    for im in (afs.get("images") or []):
                        if im.get("url"):
                            best = im.get("url")
                            break

                    # 2️⃣ Carrossel (child_attachments → image_url)
                    oss = content.get("object_story_spec") or {}

                    # 1) photo_data (foto única ou carrossel foto)
                    photo = oss.get("photo_data") or {}
                    if photo.get("image_hash"):
                        best = self._get_image_from_hash(photo["image_hash"])

                    # 2) child_attachments (funciona para foto ou link)
                    if not best:
                        children = oss.get("child_attachments") or []
                        for child in children:
                            if child.get("image_hash"):
                                best = self._get_image_from_hash(child["image_hash"])
                                break

                    # 3) link_data.child_attachments (carrossel link antigo)
                    if not best:
                        link = oss.get("link_data") or {}
                        for child in (link.get("child_attachments") or []):
                            if child.get("image_hash"):
                                best = self._get_image_from_hash(child["image_hash"])
                                break


                    # 3️⃣ Vídeos (BEST thumbnail → preview_image_url)
                    # 4) vídeos → thumbnails HD
                    if not best:
                        video_data = oss.get("video_data") or {}
                        if video_data.get("video_id"):
                            best = self._get_best_video_thumbnail(video_data["video_id"])

                    creative_image_map[str(cid)] = best

            except Exception as e:
                print("Erro ao buscar creatives batch:", e)
                continue


        # 3) mapear para df
        df["ad_image_hd"] = df["ad_id"].astype(str).map(lambda a: creative_image_map.get(ad_to_creative.get(a)))
        return df

    def _get_image_from_hash(self, image_hash):
        url = f"https://graph.facebook.com/v24.0/{image_hash}"
        params = {
            "access_token": self.access_token,
            "fields": "url"
        }
        r = requests.get(url, params=params).json()
        return r.get("url")

    def _get_best_video_thumbnail(self, video_id):
        url = f"https://graph.facebook.com/v24.0/{video_id}"
        params = {
            "access_token": self.access_token,
            "fields": "thumbnails"
        }
        js = requests.get(url, params=params).json()
        
        thumbs = js.get("thumbnails", {}).get("data", [])
        if not thumbs:
            return None
        
        # pega a maior resolução
        best = max(thumbs, key=lambda x: x.get("width", 0))
        return best.get("uri")

