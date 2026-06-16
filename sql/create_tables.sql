CREATE DATABASE IF NOT EXISTS enem_dw
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE enem_dw;

-- ============================================================
-- DESABILITAR CHECKS DURANTE CRIAÇÃO
-- ============================================================
SET FOREIGN_KEY_CHECKS = 0;
SET UNIQUE_CHECKS = 0;
SET SQL_MODE = '';

DROP TABLE IF EXISTS fato_resultados;
DROP TABLE IF EXISTS dim_socioeconomica;
DROP TABLE IF EXISTS dim_local_prova;
DROP TABLE IF EXISTS dim_escola;
DROP TABLE IF EXISTS dim_candidato;

-- ============================================================
-- DIMENSÃO CANDIDATO
-- ============================================================
CREATE TABLE dim_candidato (
    sk_candidato      BIGINT       NOT NULL,
    nu_inscricao      BIGINT       NOT NULL,
    nu_ano            SMALLINT,
    tp_faixa_etaria   TINYINT,
    ds_faixa_etaria   VARCHAR(50),
    tp_sexo           CHAR(1),
    ds_sexo           VARCHAR(10),
    tp_estado_civil   TINYINT,
    tp_cor_raca       TINYINT,
    ds_cor_raca       VARCHAR(30),
    tp_nacionalidade  TINYINT,
    tp_st_conclusao   TINYINT,
    tp_ano_concluiu   SMALLINT,
    tp_escola         TINYINT,
    tp_ensino         TINYINT,
    in_treineiro      TINYINT,

    PRIMARY KEY (sk_candidato),
    UNIQUE KEY uq_nu_inscricao (nu_inscricao),
    KEY idx_tp_sexo (tp_sexo),
    KEY idx_tp_cor_raca (tp_cor_raca),
    KEY idx_tp_faixa_etaria (tp_faixa_etaria),
    KEY idx_nu_ano (nu_ano)
) ENGINE=InnoDB
  ROW_FORMAT=COMPRESSED
  KEY_BLOCK_SIZE=8;

-- ============================================================
-- DIMENSÃO ESCOLA
-- ============================================================
CREATE TABLE dim_escola (
    sk_escola              BIGINT      NOT NULL,
    co_municipio_esc       INT,
    no_municipio_esc       VARCHAR(100),
    co_uf_esc              SMALLINT,
    sg_uf_esc              CHAR(2),
    tp_dependencia_adm_esc TINYINT,
    ds_dependencia_adm_esc VARCHAR(20),
    tp_localizacao_esc     TINYINT,
    ds_localizacao_esc     VARCHAR(20),
    tp_sit_func_esc        TINYINT,
    ds_sit_func_esc        VARCHAR(40),

    PRIMARY KEY (sk_escola),
    KEY idx_sg_uf_esc (sg_uf_esc),
    KEY idx_tp_dependencia (tp_dependencia_adm_esc),
    KEY idx_co_municipio_esc (co_municipio_esc)
) ENGINE=InnoDB
  ROW_FORMAT=COMPRESSED
  KEY_BLOCK_SIZE=8;

-- ============================================================
-- DIMENSÃO LOCAL DE PROVA
-- ============================================================
CREATE TABLE dim_local_prova (
    sk_local_prova    BIGINT   NOT NULL,
    co_municipio_prova INT,
    no_municipio_prova VARCHAR(100),
    co_uf_prova        SMALLINT,
    sg_uf_prova        CHAR(2),

    PRIMARY KEY (sk_local_prova),
    KEY idx_sg_uf_prova (sg_uf_prova),
    KEY idx_co_municipio_prova (co_municipio_prova)
) ENGINE=InnoDB
  ROW_FORMAT=COMPRESSED
  KEY_BLOCK_SIZE=8;

-- ============================================================
-- DIMENSÃO SOCIOECONÔMICA
-- ============================================================
CREATE TABLE dim_socioeconomica (
    sk_socioeconomica BIGINT NOT NULL,
    q001 CHAR(1), q002 CHAR(1), q003 CHAR(1), q004 CHAR(1),
    q005 TINYINT,
    q006 CHAR(1), q007 CHAR(1), q008 CHAR(1), q009 CHAR(1),
    q010 CHAR(1), q011 CHAR(1), q012 CHAR(1), q013 CHAR(1),
    q014 CHAR(1), q015 CHAR(1), q016 CHAR(1), q017 CHAR(1),
    q018 CHAR(1), q019 CHAR(1), q020 CHAR(1), q021 CHAR(1),
    q022 CHAR(1), q023 CHAR(1), q024 CHAR(1), q025 CHAR(1),

    PRIMARY KEY (sk_socioeconomica),
    -- Índices nas perguntas mais usadas em análises socioeconômicas
    KEY idx_q001 (q001),   -- Escolaridade pai
    KEY idx_q002 (q002),   -- Escolaridade mãe
    KEY idx_q006 (q006)    -- Renda familiar
) ENGINE=InnoDB
  ROW_FORMAT=COMPRESSED
  KEY_BLOCK_SIZE=8;

-- ============================================================
-- TABELA FATO
-- Sem AUTO_INCREMENT: sk gerado pelo Spark via row_number()
-- Sem FK declaradas: validação feita na camada ETL
-- Particionada por UF de prova para queries regionais
-- ============================================================
CREATE TABLE fato_resultados (
    sk_resultado      BIGINT        NOT NULL,
    sk_candidato      BIGINT        NOT NULL,
    sk_escola         BIGINT,
    sk_local_prova    BIGINT        NOT NULL,
    sk_socioeconomica BIGINT        NOT NULL,

    -- Presença
    tp_presenca_cn    TINYINT,
    tp_presenca_ch    TINYINT,
    tp_presenca_lc    TINYINT,
    tp_presenca_mt    TINYINT,

    -- Provas
    co_prova_cn       SMALLINT,
    co_prova_ch       SMALLINT,
    co_prova_lc       SMALLINT,
    co_prova_mt       SMALLINT,

    tp_lingua         TINYINT,
    ds_lingua         VARCHAR(10),

    -- Notas objetivas
    nu_nota_cn        DECIMAL(6,2),
    nu_nota_ch        DECIMAL(6,2),
    nu_nota_lc        DECIMAL(6,2),
    nu_nota_mt        DECIMAL(6,2),

    -- Redação
    tp_status_redacao TINYINT,
    ds_status_redacao VARCHAR(40),
    nu_nota_comp1     DECIMAL(6,2),
    nu_nota_comp2     DECIMAL(6,2),
    nu_nota_comp3     DECIMAL(6,2),
    nu_nota_comp4     DECIMAL(6,2),
    nu_nota_comp5     DECIMAL(6,2),
    nu_nota_redacao   DECIMAL(6,2),

    -- Métricas calculadas
    nota_total        DECIMAL(7,2),
    nota_media        DECIMAL(6,2),

    -- Flags
    fl_ausente        TINYINT(1)    NOT NULL DEFAULT 0,
    fl_eliminado      TINYINT(1)    NOT NULL DEFAULT 0,

    PRIMARY KEY (sk_resultado),

    -- Índices para os JOINs com dimensões
    KEY idx_sk_candidato      (sk_candidato),
    KEY idx_sk_escola         (sk_escola),
    KEY idx_sk_local_prova    (sk_local_prova),
    KEY idx_sk_socioeconomica (sk_socioeconomica),

    -- Índices para filtros analíticos comuns
    KEY idx_nota_media   (nota_media),
    KEY idx_nota_redacao (nu_nota_redacao),
    KEY idx_fl_ausente   (fl_ausente),
    KEY idx_fl_eliminado (fl_eliminado),
    KEY idx_tp_lingua    (tp_lingua),

    -- Índice composto: UF + nota_media (queries regionais de desempenho)
    KEY idx_local_media  (sk_local_prova, nota_media)

) ENGINE=InnoDB
  ROW_FORMAT=COMPRESSED
  KEY_BLOCK_SIZE=8;

-- ============================================================
-- REABILITAR CHECKS
-- ============================================================
SET FOREIGN_KEY_CHECKS = 1;
SET UNIQUE_CHECKS = 1;