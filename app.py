import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt  # Importe o matplotlib, mesmo que não use diretamente no Streamlit
from datetime import datetime

st.title("Qualidade do Ar em Tempo Real")

lat = st.text_input("Latitude", '-21.131641716582518')
lon = st.text_input("Longitude", '-42.363723220344596')

start_date = st.date_input("Data de Início", datetime(2024, 12, 14))
end_date = st.date_input("Data de Fim", datetime(2024, 12, 20))

api_key = st.text_input("Chave da Api OpenWeather", type="password",)

if st.button("Obter Dados"):
    if not api_key:
        st.error("Por favor, insira a chave da API.")
    else:
        try:
            start = int(datetime.combine(start_date, datetime.min.time()).timestamp())
            end = int(datetime.combine(end_date, datetime.max.time()).timestamp())

            url = f'http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start}&end={end}&appid={api_key}'
            response = requests.get(url)
            data = response.json()

            # Tratamento dos dados da API e criação do DataFrame
            if data and data['list']:  # Verifica se a resposta da API contém dados
                air_quality_data = []
                for item in data['list']:
                    timestamp = datetime.fromtimestamp(item['dt'])
                    components = item['components']
                    air_quality_data.append({
                        'timestamp': timestamp,
                        'co': components.get('co', None),  # Usando .get() para evitar KeyError
                        'no': components.get('no', None),
                        'no2': components.get('no2', None),
                        'o3': components.get('o3', None),
                        'so2': components.get('so2', None),
                        'pm2_5': components.get('pm2_5', None),
                        'pm10': components.get('pm10', None),
                        'nh3': components.get('nh3', None)
                    })

                df = pd.DataFrame(air_quality_data)

                # Calcular a média dos indicadores (tratando valores ausentes)
                numeric_cols = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
                df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce') # Converte para numérico e trata erros
                df['media'] = df[numeric_cols].mean(axis=1)

                # Plotagem do gráfico com Streamlit
                st.line_chart(df.set_index('timestamp')['media'])

                # Encontrar o horário de pico (tratando valores ausentes)
                pico = df.loc[df['media'].idxmax()]
                st.write(f"Horário de pico: {pico['timestamp']} com média de {pico['media']:.2f}")

            else:
                st.warning("Não foram encontrados dados para o período selecionado ou a API retornou um erro.")

        except requests.exceptions.RequestException as e:
            st.error(f"Erro na requisição à API: {e}")
        except (KeyError, TypeError) as e:  # Captura erros de chave ou tipo nos dados
            st.error(f"Erro ao processar dados da API. Verifique a chave da API e os dados retornados: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")