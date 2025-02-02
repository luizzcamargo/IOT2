import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns  
from datetime import datetime

st.title("Qualidade do Ar em Tempo Real")

lat = st.text_input("Latitude", '-21.131641716582518')
lon = st.text_input("Longitude", '-42.363723220344596')

start_date = st.date_input("Data de Início", datetime(2024, 12, 14))
end_date = st.date_input("Data de Fim", datetime(2024, 12, 20))

api_key = st.text_input("Chave da Api OpenWeather","77b64cb2c7a3e0032fabcaa48c784f8b", type="password",)

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

            if data and data['list']:
                air_quality_data = []
                for item in data['list']:
                    timestamp = datetime.fromtimestamp(item['dt'])
                    components = item['components']
                    air_quality_data.append({
                        'timestamp': timestamp,
                        'co': components.get('co', None),
                        'no': components.get('no', None),
                        'no2': components.get('no2', None),
                        'o3': components.get('o3', None),
                        'so2': components.get('so2', None),
                        'pm2_5': components.get('pm2_5', None),
                        'pm10': components.get('pm10', None),
                        'nh3': components.get('nh3', None)
                    })

                df = pd.DataFrame(air_quality_data)

                numeric_cols = ['co', 'no', 'no2', 'o3', 'so2', 'pm2_5', 'pm10', 'nh3']
                df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
                df['media'] = df[numeric_cols].mean(axis=1)

                # Classificação da qualidade do ar
                def classificar_qualidade(media):
                    if media < 50:
                        return 'Boa'
                    elif media < 100:
                        return 'Moderada'
                    elif media < 150:
                        return 'Ruim'
                    else:
                        return 'Péssima'

                df['classificacao'] = df['media'].apply(classificar_qualidade)
                
                
                st.subheader(" 2 - Histório da Qualidade do Ar")
                
                # Gráfico de linha da média
                st.line_chart(df.set_index('timestamp')['media'])

                # Exibir a classificação média dos indicadores
                st.subheader("3 - Local de Interesse - Centro da Cidade de Muriáe")
                
                st.subheader("4 - Classificação Média dos Indicadores do Ar")

                indicadores = {
                    'CO': {'media': df['co'].mean(), 'classificacao': None},
                    'NO': {'media': df['no'].mean(), 'classificacao': None},
                    'NO2': {'media': df['no2'].mean(), 'classificacao': None},
                    'O3': {'media': df['o3'].mean(), 'classificacao': None},
                    'SO2': {'media': df['so2'].mean(), 'classificacao': None},
                    'PM2.5': {'media': df['pm2_5'].mean(), 'classificacao': None},
                    'PM10': {'media': df['pm10'].mean(), 'classificacao': None},
                    'NH3': {'media': df['nh3'].mean(), 'classificacao': None}
                }
                for indicador, valores in indicadores.items():
                    if pd.notna(valores['media']):
                        valores['classificacao'] = classificar_qualidade(valores['media'])
                    else:
                        valores['classificacao'] = "Não disponível"

                for indicador, valores in indicadores.items():
                    st.write(f"{indicador}: Média = {valores['media']:.2f}, Classificação = {valores['classificacao']}")

                # Gráfico de barras da classificação geral
                classificacoes = df['classificacao'].value_counts().sort_index()
                st.bar_chart(classificacoes)
                
                st.subheader("5 - Hoário de Pico do Ponto de Interesse")

                # Horário de pico
                try:
                    pico = df.loc[df['media'].idxmax()]
                    st.write(f"Horário de pico: {pico['timestamp']} com média de {pico['media']:.2f}")
                except ValueError:
                    st.warning("Não foi possível determinar o horário de pico. Dados insuficientes.")

                # Correlação entre indicadores
                st.subheader("6 - Correlação entre Indicadores")

                correlacao = df[numeric_cols].corr()
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(correlacao, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
                ax.set_title("Matriz de Correlação entre Indicadores")
                st.pyplot(fig)

                # Variação diária dos indicadores
                st.subheader("7 - Variação Diária dos Indicadores")
                df['dia_semana'] = df['timestamp'].dt.dayofweek
                df['hora'] = df['timestamp'].dt.hour

                media_hora = df.groupby('hora')[numeric_cols].mean()
                st.line_chart(media_hora)

                # Variação semanal dos indicadores
                st.subheader("8 - Variação Semanal dos Indicadores")
                media_dia_semana = df.groupby('dia_semana')[numeric_cols].mean()
                st.line_chart(media_dia_semana)

            else:
                st.warning("Não foram encontrados dados para o período selecionado ou a API retornou um erro.")

        except requests.exceptions.RequestException as e:
            st.error(f"Erro na requisição à API: {e}")
        except (KeyError, TypeError) as e:
            st.error(f"Erro ao processar dados da API. Verifique a chave da API e os dados retornados: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
