import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import random as rn
from wordcloud import WordCloud
import plotly.graph_objects as go
from funcs import *

st.set_page_config(
    page_title="Análise de sentimentos em avaliações de jogos na Steam",
    page_icon="✅",
    layout="centered",
)

def build_header():
    st.title("Análise de sentimentos em avaliações de jogos na Steam")

    st.markdown("---")

def build_body():

    # pega_df1 = carrega_df('df1')
    # dfs = pd.merge(pega_df1, pega_df2, left_\\\\\\\\\\on="app_id", right_on="app_id", suffixes=("_df1", "_df2"))
    # # Remove a coluna app_id_df2
    # dfs.drop(dfs.columns[5:6], axis=1, inplace=True)

    ocultar_df = st.sidebar.checkbox('Ocultar conjunto de dados')

    if ocultar_df:
        st.sidebar.write('Conjunto de dados ocultado')

    else:
        st.header('Visão geral do conjunto de dados')
        st.text("")
        pega_df2 = carrega_df('df2')
        pega_df2 = pega_df2.rename(columns={'app_id_df2': 'id', 'app_name_df2': 'nome', 'release_date': 'Lançamento',
                                            'developer': 'Desenvolvedor', 'publisher': 'Publicador', 'platforms': 'Plataforma',
                                            'required_age': 'Faixa etária', 'categories': 'Categorias', 'genres': 'Gêneros',
                                            'steamspy_tags' : 'Tags da Steam', 'achievements': 'Conquistas', 
                                            'positive_ratings': 'Avaliações positivas', 'negative_ratings': 'Avaliações Negativas',
                                            'owners': 'Donos?', 'price': 'Preço'})
        st.dataframe(pega_df2, hide_index=True)
        st.caption('A tabela acima apresenta os dados gerais do jogos utilizados durante o trabalho. Seus dados são provenientes do segundo dataframe.')
        st.text("")

    st.header("Estatíscas gerais dos conjuntos de dados")
    st.text("")

    col1, col2 = st.columns(2)

    with col1:
        carrega_df2_app_id = carrega_coluna('app_id_df2')
        qtd_jogos = len(carrega_df2_app_id) - 1

        carrega_df1_app_id = carrega_coluna('app_id')
        qtd_reviews = len(carrega_df1_app_id) - 1

        qtd_jogos_formatado = '{:,.0f}'.format(qtd_jogos).replace(',', '.')
        qtd_reviews_formatado = '{:,.0f}'.format(qtd_reviews).replace(',', '.')

        st.write('Quantidade total de jogos: %s' % qtd_jogos_formatado)
        st.write('Quantidade total de avaliações: %s' % qtd_reviews_formatado)

    with col2: 
        merged_id_e_review = mistura_colunas('app_id', 'review_text')

        # Calcula a média de reviews por jogo
        media_reviews = merged_id_e_review.groupby('app_id')['app_id'].count().mean()

        media_reviews_formatado = '{:.2f}'.format(round(media_reviews, 2)).replace('.', ',')

        st.write('Quantidade média de avaliações por jogo: %s' % media_reviews_formatado)
    
    graph_options = {"Histograma de sentimentos":'grafico1', "Histograma de contagem de reviews recomendados por sentimento":'grafico2', "Gráfico de pizza de distribuição de sentimentos":'grafico3', "Gráfico de correlação: Polaridade média vs Quantidade média de Jogadores":'grafico4',
        "Histograma dos 10 jogos com mais reviews":'grafico0'}
    st.text("")
    st.subheader("Use o seletor para analisar todo do conjunto de dados:")
    st.text("")
    selected_chart = st.selectbox('Selecione um grafico: ', graph_options)

    for nome_funcao, graficos in graph_options.items():
        if graficos == selected_chart:
            chama_funcao = globals()[graficos]
            chama_funcao()
    
    # Os gráficos estavam chamando os dataframes pelas variáveis abaixo
    df = 1
    df_tags = 1

def grafico0():
    # Esse é o gráfico bichado lá

    st.subheader("Histograma dos 10 jogos com mais reviews") 
    dados_jogos = df.groupby(["app_id", "app_name", "review_score"]).agg({"review_text": "count"}).reset_index()
    dados_jogos = dados_jogos.rename(columns={"review_text": "review_count"})
    top10_jogos = dados_jogos.groupby(["app_id", "app_name"]).agg({"review_count": "sum"}).sort_values("review_count", ascending=False).head(10).reset_index()
    dados_jogos = dados_jogos[dados_jogos["app_id"].isin(top10_jogos["app_id"])]
    barras_horizontal = px.bar(dados_jogos, y="app_name", x="review_count", color="review_score", orientation="h",
                hover_data=["review_count"], category_orders={"app_name": top10_jogos["app_name"]})
    barras_horizontal.update_layout(
    #title="Os 10 jogos com mais reviews",
    xaxis_title="Número de reviews",
    yaxis_title="Jogo",
    legend_title="Sentimento",
    width=1000,
    height=600,
    margin=dict(l=50, r=50, t=80, b=80),
    hovermode="closest")
    st.plotly_chart(barras_horizontal)
    st.write("Representação gráfica dos 10 jogos com mais reviews, a sua distribuição de sentimento e o número de reviews")

def grafico1():

    st.subheader("Histograma de sentimentos")
    st.write('')
    histograma_sentimentos = go.Figure(data=[
        go.Bar(
            x=['Negativa', 'Positiva'],
            y=df['review_score'].value_counts(),
            marker=dict(
                color=['#FF4136', '#2ECC40'],
                line=dict(color='#000000', width=1)
            )
        )
    ])

    histograma_sentimentos.update_layout(
        title='Histograma de sentimentos',
        xaxis_title='Polaridade da review',
        yaxis_title='Contagem de registros'
    )

    st.plotly_chart(histograma_sentimentos)
    st.write("Representação gráfica da distribuição de sentimentos em reviews de jogos da Steam")

def grafico2():

    st.subheader("Histograma de contagem de reviews recomendados por sentimento")
    sentiment_votes = df.groupby(['review_score', 'review_votes'])['app_id'].count().unstack('review_votes')

    sentiment_votes = sentiment_votes.rename(columns={0: 'Review não recomendada', 1: 'Review recomendada'})
    sentiment_votes = sentiment_votes.rename(index={-1: 'Negativo', 1: 'Positivo'})

    colors = ['#FF4136', '#2ECC40']

    barras_agrupadas = go.Figure(data=[
        go.Bar(name='Review não recomendada', x=sentiment_votes.index, y=sentiment_votes['Review não recomendada'], 
            marker=dict(color=colors[0])),
        go.Bar(name='Review recomendada', x=sentiment_votes.index, y=sentiment_votes['Review recomendada'], 
            marker=dict(color=colors[1]))
    ])

    barras_agrupadas.update_layout(
        title='Contagem de reviews recomendadas e não recomendadas por sentimento',
        xaxis_title='Sentimento',
        yaxis_title='Contagem de registros',
        barmode='stack'
    )

    st.plotly_chart(barras_agrupadas)
    st.write("Representação gráfica da contagem de reviews recomendadas e não recomendadas por sentimento")

def grafico3():

    st.subheader("Gráfico de pizza de distribuição de sentimentos")

    sentiment_colors = {-1: '#FF4136', 1: '#2ECC40'}

    pizza_chart = px.pie(df, values='review_votes', names='review_score', color='review_score',
                        color_discrete_map=sentiment_colors)

    pizza_chart.update_layout(
        legend_title="Sentimento",
        width=1000,
        height=600
    )

    pizza_chart.update_traces(marker=dict(colors=[sentiment_colors[sentiment] for sentiment in df['review_score']]))
    pizza_chart.update_layout(
        legend=dict(
            x=1.1,
            y=0.5,
            title="Sentimento",
            title_font=dict(size=14),
            itemsizing='constant'
        )
    )

    st.plotly_chart(pizza_chart)
    st.write("Representação gráfica da proporção de sentimentos positivos e negativos nas reviews")
def grafico4():

    df_merged_g4 = mistura_colunas(app_id, review_score)
    st.subheader("Gráfico de correlação: Polaridade média vs Quantidade média de Jogadores")

    #calcular a media de polaridade de reviews por jogo
    positivas = df_merged_g4.groupby('app_id')['review_score'].sum()
    reviews_totais = df_merged_g4.groupby('app_id')['review_score'].count()
    med_polaridade = ((positivas / reviews_totais) * 100).clip(lower=0)
    
    player_counts = []
    app_ids = []
    app_names = []

    #carregar os dados de contagemd e jogadores
    for app_id in med_polaridade.index:
        try:
            player_data = load_csv3(app_id)
            player_count = player_data['Playercount'].mean()
            player_counts.append(player_count)
            app_name = df_merged_g4[df_merged_g4['app_id'] == app_id]['app_name'].values[0]
            app_ids.append(app_id)
            app_names.append(app_name)
        except FileNotFoundError:
            #st.write(f"Aviso: Nenhum dado de qtd. de jogadores para o ID encontrado: {app_id}")  #pular jogos sem dados de playercount
            pass

    #df com a player count de cada jogo
    player_df = pd.DataFrame({'app_id': app_ids, 'app_name': app_names, 'player_count': player_counts})
    #df com playercount e sentimentos
    merged_player_sentimentos_df = pd.merge(med_polaridade.reset_index(), player_df, on='app_id')

    fig = px.scatter(merged_player_sentimentos_df, x="review_score", y="player_count",
                     title='Correlação entre a polaridade média das reviews e a quantidade média de jogadores',
                     labels={'review_score':'Média das reviews (%)', 'player_count':'Quantidade média de jogadores'},
                     hover_data=['app_name'],
                     color='review_score',            
                     color_continuous_scale=[(0, "red"),(1, "green")])
    st.plotly_chart(fig)


build_header()
build_body()
