USE enem_dw;

-- 1. Grupo escolar com maior média de notas
-- Observação:
-- município + UF + dependência administrativa + localização.

SELECT
    e.co_municipio_esc,
    e.no_municipio_esc,
    e.sg_uf_esc,
    e.ds_dependencia_adm_esc,
    e.ds_localizacao_esc,
    COUNT(*) AS total_alunos,
    ROUND(AVG(f.nota_media), 2) AS media_notas
FROM fato_resultados f
JOIN dim_escola e
    ON f.sk_escola = e.sk_escola
WHERE f.nota_media IS NOT NULL
GROUP BY
    e.co_municipio_esc,
    e.no_municipio_esc,
    e.sg_uf_esc,
    e.ds_dependencia_adm_esc,
    e.ds_localizacao_esc
ORDER BY media_notas DESC
LIMIT 1;

-- 2. Aluno com maior média de notas

SELECT
    c.nu_inscricao,
    c.ds_sexo,
    c.ds_cor_raca,
    c.ds_faixa_etaria,
    ROUND(f.nota_media, 2) AS media_notas,
    ROUND(f.nota_total, 2) AS nota_total
FROM fato_resultados f
JOIN dim_candidato c
    ON f.sk_candidato = c.sk_candidato
WHERE f.nota_media IS NOT NULL
ORDER BY f.nota_media DESC
LIMIT 1;

-- 3. Média geral

SELECT
    ROUND(AVG(nota_media), 2) AS media_geral
FROM fato_resultados
WHERE nota_media IS NOT NULL;


-- 4. Percentual de ausentes

SELECT
    COUNT(*) AS total_registros,
    SUM(CASE WHEN fl_ausente = 1 THEN 1 ELSE 0 END) AS total_ausentes,
    ROUND(
        100.0 * SUM(CASE WHEN fl_ausente = 1 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS percentual_ausentes
FROM fato_resultados;


-- 5. Número total de inscritos

SELECT
    COUNT(DISTINCT nu_inscricao) AS total_inscritos
FROM dim_candidato;


-- 6. Média por disciplina

SELECT
    ROUND(AVG(nu_nota_cn), 2) AS media_ciencias_natureza,
    ROUND(AVG(nu_nota_ch), 2) AS media_ciencias_humanas,
    ROUND(AVG(nu_nota_lc), 2) AS media_linguagens_codigos,
    ROUND(AVG(nu_nota_mt), 2) AS media_matematica,
    ROUND(AVG(nu_nota_redacao), 2) AS media_redacao
FROM fato_resultados;


-- 7. Média por sexo

SELECT
    c.ds_sexo,
    COUNT(*) AS total_alunos,
    ROUND(AVG(f.nota_media), 2) AS media_notas
FROM fato_resultados f
JOIN dim_candidato c
    ON f.sk_candidato = c.sk_candidato
WHERE f.nota_media IS NOT NULL
GROUP BY c.ds_sexo
ORDER BY media_notas DESC;

-- 8. Média por etnia / cor-raça

SELECT
    c.tp_cor_raca,
    c.ds_cor_raca,
    COUNT(*) AS total_alunos,
    ROUND(AVG(f.nota_media), 2) AS media_notas
FROM fato_resultados f
JOIN dim_candidato c
    ON f.sk_candidato = c.sk_candidato
WHERE f.nota_media IS NOT NULL
GROUP BY
    c.tp_cor_raca,
    c.ds_cor_raca
ORDER BY media_notas DESC;

-- 9. Média por faixa etária

SELECT
    c.tp_faixa_etaria,
    c.ds_faixa_etaria,
    COUNT(*) AS total_alunos,
    ROUND(AVG(f.nota_media), 2) AS media_notas
FROM fato_resultados f
JOIN dim_candidato c
    ON f.sk_candidato = c.sk_candidato
WHERE f.nota_media IS NOT NULL
GROUP BY
    c.tp_faixa_etaria,
    c.ds_faixa_etaria
ORDER BY c.tp_faixa_etaria;


-- 10. Média por dependência administrativa da escola

SELECT
    e.ds_dependencia_adm_esc,
    COUNT(*) AS total_alunos,
    ROUND(AVG(f.nota_media), 2) AS media_notas
FROM fato_resultados f
JOIN dim_escola e
    ON f.sk_escola = e.sk_escola
WHERE f.nota_media IS NOT NULL
GROUP BY e.ds_dependencia_adm_esc
ORDER BY media_notas DESC;