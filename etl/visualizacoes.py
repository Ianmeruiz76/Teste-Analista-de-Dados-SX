import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine


DB_HOST = "localhost"
DB_PORT = 3308
DB_NAME = "enem_dw"
DB_USER = "root"
DB_PASSWORD = "root"

OUTPUT_DIR = "outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def salvar_csv(df, nome):
    caminho = os.path.join(OUTPUT_DIR, f"{nome}.csv")
    df.to_csv(caminho, index=False, encoding="utf-8-sig")
    print(f"CSV gerado: {caminho}")


def salvar_grafico_barras(df, x, y, titulo, nome, rotacao=45):
    df = df.copy()

    if df.empty:
        print(f"Sem dados para gerar gráfico: {nome}")
        return

    df[x] = df[x].fillna("Não informado").astype(str)
    df[y] = pd.to_numeric(df[y], errors="coerce").fillna(0)

    df = df[df[y] > 0]

    if df.empty:
        print(f"Sem dados válidos para gerar gráfico: {nome}")
        return

    plt.figure(figsize=(10, 6))
    plt.bar(df[x], df[y])
    plt.title(titulo)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.xticks(rotation=rotacao, ha="right")
    plt.tight_layout()

    caminho = os.path.join(OUTPUT_DIR, f"{nome}.png")
    plt.savefig(caminho, dpi=300)
    plt.close()

    print(f"Gráfico gerado: {caminho}")


def salvar_histograma(df, coluna, titulo, nome):
    df = df.copy()

    if df.empty:
        print(f"Sem dados para gerar histograma: {nome}")
        return

    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    df = df[df[coluna].notnull()]

    if df.empty:
        print(f"Sem dados válidos para gerar histograma: {nome}")
        return

    plt.figure(figsize=(10, 6))
    plt.hist(df[coluna], bins=30)
    plt.title(titulo)
    plt.xlabel(coluna)
    plt.ylabel("Frequência")
    plt.tight_layout()

    caminho = os.path.join(OUTPUT_DIR, f"{nome}.png")
    plt.savefig(caminho, dpi=300)
    plt.close()

    print(f"Gráfico gerado: {caminho}")


def executar_consulta(nome, query):
    df = pd.read_sql(query, engine)
    salvar_csv(df, nome)
    return df


def main():
    print("Gerando bases e gráficos...")

    # 1. Média por sexo
    df_sexo = executar_consulta(
        "media_por_sexo",
        """
        SELECT
            COALESCE(c.ds_sexo, 'Não informado') AS sexo,
            COUNT(*) AS total_alunos,
            ROUND(AVG(f.nota_media), 2) AS media_notas
        FROM fato_resultados f
        JOIN dim_candidato c
            ON f.sk_candidato = c.sk_candidato
        WHERE f.nota_media IS NOT NULL
        GROUP BY COALESCE(c.ds_sexo, 'Não informado')
        ORDER BY media_notas DESC;
        """
    )

    salvar_grafico_barras(
        df_sexo,
        "sexo",
        "media_notas",
        "Média de Notas por Sexo",
        "media_por_sexo",
        rotacao=0
    )

    # 2. Média por cor/raça
    df_raca = executar_consulta(
        "media_por_raca",
        """
        SELECT
            COALESCE(c.ds_cor_raca, 'Não informado') AS cor_raca,
            COUNT(*) AS total_alunos,
            ROUND(AVG(f.nota_media), 2) AS media_notas
        FROM fato_resultados f
        JOIN dim_candidato c
            ON f.sk_candidato = c.sk_candidato
        WHERE f.nota_media IS NOT NULL
        GROUP BY COALESCE(c.ds_cor_raca, 'Não informado')
        ORDER BY media_notas DESC;
        """
    )

    salvar_grafico_barras(
        df_raca,
        "cor_raca",
        "media_notas",
        "Média de Notas por Cor/Raça",
        "media_por_raca"
    )

    # 3. Média por faixa etária
    df_faixa = executar_consulta(
        "media_por_faixa_etaria",
        """
        SELECT
            c.tp_faixa_etaria,
            COALESCE(c.ds_faixa_etaria, 'Não informado') AS faixa_etaria,
            COUNT(*) AS total_alunos,
            ROUND(AVG(f.nota_media), 2) AS media_notas
        FROM fato_resultados f
        JOIN dim_candidato c
            ON f.sk_candidato = c.sk_candidato
        WHERE f.nota_media IS NOT NULL
        GROUP BY
            c.tp_faixa_etaria,
            COALESCE(c.ds_faixa_etaria, 'Não informado')
        ORDER BY c.tp_faixa_etaria;
        """
    )

    salvar_grafico_barras(
        df_faixa,
        "faixa_etaria",
        "media_notas",
        "Média de Notas por Faixa Etária",
        "media_por_faixa_etaria"
    )

    # 4. Média por disciplina
    df_disciplina = executar_consulta(
        "media_por_disciplina",
        """
        SELECT 'Ciências da Natureza' AS disciplina, ROUND(AVG(nu_nota_cn), 2) AS media
        FROM fato_resultados
        UNION ALL
        SELECT 'Ciências Humanas', ROUND(AVG(nu_nota_ch), 2)
        FROM fato_resultados
        UNION ALL
        SELECT 'Linguagens', ROUND(AVG(nu_nota_lc), 2)
        FROM fato_resultados
        UNION ALL
        SELECT 'Matemática', ROUND(AVG(nu_nota_mt), 2)
        FROM fato_resultados
        UNION ALL
        SELECT 'Redação', ROUND(AVG(nu_nota_redacao), 2)
        FROM fato_resultados;
        """
    )

    salvar_grafico_barras(
        df_disciplina,
        "disciplina",
        "media",
        "Média por Disciplina",
        "media_por_disciplina"
    )

    # 5. Média por dependência administrativa da escola
    df_dependencia = executar_consulta(
        "media_por_dependencia_escola",
        """
        SELECT
            COALESCE(e.ds_dependencia_adm_esc, 'Não informado') AS dependencia,
            COUNT(*) AS total_alunos,
            ROUND(AVG(f.nota_media), 2) AS media_notas
        FROM fato_resultados f
        JOIN dim_escola e
            ON f.sk_escola = e.sk_escola
        WHERE f.nota_media IS NOT NULL
        GROUP BY COALESCE(e.ds_dependencia_adm_esc, 'Não informado')
        ORDER BY media_notas DESC;
        """
    )

    salvar_grafico_barras(
        df_dependencia,
        "dependencia",
        "media_notas",
        "Média por Dependência Administrativa da Escola",
        "media_por_dependencia_escola"
    )

    # 6. Status da redação
    df_redacao = executar_consulta(
        "redacao_por_status",
        """
        SELECT
            COALESCE(ds_status_redacao, 'Não informado') AS status_redacao,
            COUNT(*) AS total_alunos,
            ROUND(AVG(nu_nota_redacao), 2) AS media_redacao
        FROM fato_resultados
        GROUP BY COALESCE(ds_status_redacao, 'Não informado')
        ORDER BY total_alunos DESC;
        """
    )

    salvar_grafico_barras(
        df_redacao,
        "status_redacao",
        "total_alunos",
        "Quantidade de Alunos por Status da Redação",
        "redacao_por_status"
    )

    # 7. Média por UF da prova
    df_uf = executar_consulta(
        "media_por_uf_prova",
        """
        SELECT
            COALESCE(l.sg_uf_prova, 'Não informado') AS uf_prova,
            COUNT(*) AS total_alunos,
            ROUND(AVG(f.nota_media), 2) AS media_notas
        FROM fato_resultados f
        JOIN dim_local_prova l
            ON f.sk_local_prova = l.sk_local_prova
        WHERE f.nota_media IS NOT NULL
        GROUP BY COALESCE(l.sg_uf_prova, 'Não informado')
        ORDER BY media_notas DESC;
        """
    )

    salvar_grafico_barras(
        df_uf,
        "uf_prova",
        "media_notas",
        "Média de Notas por UF da Prova",
        "media_por_uf_prova"
    )

    # 8. Renda familiar Q006
    df_renda = executar_consulta(
        "media_por_renda_q006",
        """
        SELECT
            COALESCE(s.q006, 'Z') AS renda_q006,
            COUNT(*) AS total_alunos,
            ROUND(AVG(f.nota_media), 2) AS media_notas
        FROM fato_resultados f
        JOIN dim_socioeconomica s
            ON f.sk_socioeconomica = s.sk_socioeconomica
        WHERE f.nota_media IS NOT NULL
        GROUP BY COALESCE(s.q006, 'Z')
        ORDER BY renda_q006;
        """
    )

    salvar_grafico_barras(
        df_renda,
        "renda_q006",
        "media_notas",
        "Média de Notas por Renda Familiar",
        "media_por_renda_q006",
        rotacao=0
    )

    # 9. Acesso à internet Q025
    df_internet = executar_consulta(
        "media_por_internet_q025",
        """
        SELECT
            COALESCE(s.q025, 'Z') AS internet_q025,
            COUNT(*) AS total_alunos,
            ROUND(AVG(f.nota_media), 2) AS media_notas
        FROM fato_resultados f
        JOIN dim_socioeconomica s
            ON f.sk_socioeconomica = s.sk_socioeconomica
        WHERE f.nota_media IS NOT NULL
        GROUP BY COALESCE(s.q025, 'Z')
        ORDER BY internet_q025;
        """
    )

    salvar_grafico_barras(
        df_internet,
        "internet_q025",
        "media_notas",
        "Média de Notas por Acesso à Internet",
        "media_por_internet_q025",
        rotacao=0
    )

    # 10. Distribuição da nota média
    df_distribuicao = executar_consulta(
        "distribuicao_nota_media",
        """
        SELECT
            nota_media
        FROM fato_resultados
        WHERE nota_media IS NOT NULL;
        """
    )

    salvar_histograma(
        df_distribuicao,
        "nota_media",
        "Distribuição da Nota Média",
        "distribuicao_nota_media"
    )

    # 11. Correlação entre notas
    df_corr = pd.read_sql(
        """
        SELECT
            nu_nota_cn,
            nu_nota_ch,
            nu_nota_lc,
            nu_nota_mt,
            nu_nota_redacao,
            nota_total,
            nota_media
        FROM fato_resultados
        WHERE nota_media IS NOT NULL;
        """,
        engine
    )

    if not df_corr.empty:
        matriz_corr = df_corr.corr(numeric_only=True).round(2)

        caminho_corr = os.path.join(OUTPUT_DIR, "correlacao_notas.csv")
        matriz_corr.to_csv(caminho_corr, encoding="utf-8-sig")
        print(f"Correlação gerada: {caminho_corr}")

        plt.figure(figsize=(8, 6))
        plt.imshow(matriz_corr, aspect="auto")
        plt.colorbar()
        plt.xticks(
            range(len(matriz_corr.columns)),
            matriz_corr.columns,
            rotation=45,
            ha="right"
        )
        plt.yticks(
            range(len(matriz_corr.index)),
            matriz_corr.index
        )
        plt.title("Correlação entre Notas")
        plt.tight_layout()

        caminho_heatmap = os.path.join(OUTPUT_DIR, "correlacao_notas.png")
        plt.savefig(caminho_heatmap, dpi=300)
        plt.close()

        print(f"Gráfico gerado: {caminho_heatmap}")
    else:
        print("Sem dados para gerar correlação.")

    print("Visualizações geradas com sucesso.")


if __name__ == "__main__":
    main()