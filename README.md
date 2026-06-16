# Análise dos Microdados do ENEM 2020

## 1. Objetivo do Projeto

Este projeto tem como objetivo realizar o processamento, modelagem e análise dos Microdados do ENEM 2020, utilizando uma arquitetura baseada em ETL, modelagem dimensional e armazenamento em banco de dados MySQL executado em container Docker.

A proposta consiste em transformar a base bruta disponibilizada pelo INEP em um modelo analítico estruturado, permitindo a geração de indicadores, consultas SQL, análises exploratórias e, posteriormente, visualizações e dashboard.

O projeto foi desenvolvido como parte de um teste técnico para a área de Análise de Dados, contemplando os seguintes pontos:

* Organização do código
* Docker
* SQL
* Python
* PySpark
* ETL
* Modelagem dimensional
* Banco de dados MySQL
* Documentação técnica
* Preparação para análises e visualizações

---

## 2. Base de Dados

A base utilizada corresponde aos Microdados do ENEM 2020.

Após o download e descompactação dos arquivos originais, o arquivo principal utilizado no processo de ETL é:

```text
microdados_enem_2020/DADOS/MICRODADOS_ENEM_2020.csv
```

No projeto, a base foi posicionada no diretório:

```text
data/MICRODADOS_ENEM_2020.csv
```

A documentação dos campos foi consultada a partir do dicionário de dados oficial disponibilizado junto aos microdados.

---

## 3. Tecnologias Utilizadas

As principais tecnologias utilizadas no projeto são:

* Python
* PySpark
* MySQL
* Docker
* Docker Compose
* SQL
* Pandas
* PowerShell
* VS Code

Bibliotecas Python utilizadas:

```text
pandas
numpy
pyspark
sqlalchemy
pymysql
python-dotenv
matplotlib
seaborn
plotly
```

---

## 4. Estrutura do Projeto

A estrutura do projeto foi organizada da seguinte forma:

```text
Teste-Analista-de-Dados-SX/
├── README.md
├── requirements.txt
├── .gitignore
├── docker-compose.yml
├── data/
│   └── MICRODADOS_ENEM_2020.csv
├── sql/
│   ├── create_tables.sql
│   └── indicadores.sql
├── etl/
│   ├── main.py
│   ├── spark_session.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── notebooks/
├── dashboard/
└── outputs/
```

### Descrição dos principais diretórios

| Diretório    | Descrição                                                                         |
| ------------ | --------------------------------------------------------------------------------- |
| `data/`      | Armazena a base bruta do ENEM 2020.                                               |
| `etl/`       | Contém os scripts responsáveis pela extração, transformação e carga dos dados.    |
| `sql/`       | Contém os scripts de criação das tabelas e consultas de indicadores.              |
| `outputs/`   | Diretório reservado para arquivos exportados, agregações e resultados analíticos. |
| `dashboard/` | Diretório reservado para arquivos de dashboard e visualizações finais.            |
| `notebooks/` | Diretório reservado para análises exploratórias, se necessário.                   |

---

## 5. Ambiente com Docker

O banco de dados MySQL é executado em um container Docker.

Arquivo `docker-compose.yml`:

```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: enem_mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: enem_dw
    ports:
      - "3308:3306"
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

A porta externa utilizada foi `3308`, pois as portas `3306` e `3307` já estavam ocupadas no ambiente local.

Para subir o container:

```powershell
docker compose up -d
```

Para validar se o container está em execução:

```powershell
docker ps
```

Para acessar o MySQL dentro do container:

```powershell
docker exec -it enem_mysql mysql -uroot -proot
```

---

## 6. Modelagem Dimensional

Foi adotado um modelo dimensional no formato estrela, com uma tabela fato central e dimensões auxiliares.

### Tabela fato

```text
fato_resultados
```

A tabela fato concentra as informações de desempenho dos candidatos, incluindo:

* Chaves das dimensões
* Presença nas provas
* Códigos das provas
* Notas por área de conhecimento
* Notas da redação
* Nota total
* Nota média
* Flag de ausência
* Flag de eliminação

### Tabelas dimensão

```text
dim_candidato
dim_escola
dim_local_prova
dim_socioeconomica
```

### Modelo lógico

```text
dim_candidato       ┐
dim_escola          ├── fato_resultados
dim_local_prova     ┤
dim_socioeconomica  ┘
```

---

## 7. Observação Sobre a Dimensão Escola

Durante a análise do dicionário de dados, foi identificado que a base dos Microdados do ENEM 2020 utilizada neste projeto não possui um identificador individual de escola, como `CO_ESCOLA`.

Por esse motivo, a dimensão escola foi modelada a partir dos campos disponíveis relacionados à escola do participante:

```text
CO_MUNICIPIO_ESC
NO_MUNICIPIO_ESC
CO_UF_ESC
SG_UF_ESC
TP_DEPENDENCIA_ADM_ESC
TP_LOCALIZACAO_ESC
TP_SIT_FUNC_ESC
```

Dessa forma, a análise de escola é feita por agrupamento de características escolares, como município, UF, dependência administrativa, localização e situação de funcionamento.

Portanto, a pergunta "Qual a escola com a maior média de notas?" foi adaptada para responder qual grupo escolar possui a maior média de notas, considerando os campos disponíveis na base.

---

## 8. Processo de ETL

O processo de ETL foi dividido em três etapas principais:

### 8.1 Extração

A extração é feita a partir do arquivo CSV dos Microdados do ENEM 2020.

Arquivo responsável:

```text
etl/extract.py
```

A leitura considera:

* Cabeçalho
* Separador `;`
* Encoding `ISO-8859-1`
* Inferência de schema

### 8.2 Transformação

A transformação é feita no arquivo:

```text
etl/transform.py
```

As principais transformações realizadas são:

* Seleção apenas das colunas necessárias
* Padronização dos nomes das colunas
* Conversão de tipos
* Tratamento de valores nulos
* Criação de descrições para campos categóricos
* Criação das dimensões
* Criação da tabela fato
* Cálculo da nota total
* Cálculo da nota média
* Criação de flags de ausência e eliminação

### 8.3 Carga

A carga dos dados é feita no MySQL via JDBC.

Arquivo responsável:

```text
etl/load.py
```

A ordem de carga respeita a estrutura dimensional:

```text
1. dim_candidato
2. dim_escola
3. dim_local_prova
4. dim_socioeconomica
5. fato_resultados
```

As dimensões são carregadas antes da tabela fato para garantir a integridade referencial das chaves estrangeiras.

---

## 9. Tratamento de Dados

Durante o processo de transformação, foram aplicadas as seguintes regras:

### Notas

As notas nulas foram mantidas como nulas para evitar distorções nos cálculos de média.

A `nota_total` e a `nota_media` são calculadas apenas quando todas as quatro notas objetivas estão disponíveis:

```text
NU_NOTA_CN
NU_NOTA_CH
NU_NOTA_LC
NU_NOTA_MT
```

A redação é analisada separadamente por meio do campo:

```text
NU_NOTA_REDACAO
```

### Ausentes

Foi criada a flag `fl_ausente`.

Um participante é considerado ausente quando possui valor `0` em pelo menos um dos campos de presença:

```text
TP_PRESENCA_CN
TP_PRESENCA_CH
TP_PRESENCA_LC
TP_PRESENCA_MT
```

### Eliminados

Foi criada a flag `fl_eliminado`.

Um participante é considerado eliminado quando possui valor `2` em pelo menos um dos campos de presença.

### Questionário socioeconômico

Os campos do questionário socioeconômico foram tratados da seguinte forma:

* Respostas nulas em campos categóricos foram substituídas por `Z`.
* O campo `Q005`, por ser numérico, recebeu `0` quando nulo.

Campos utilizados:

```text
Q001 até Q025
```

---

## 10. Otimização do Processamento

Durante a execução com a base completa, foi identificado erro de memória no Spark:

```text
java.lang.OutOfMemoryError: Java heap space
```

A causa principal estava relacionada ao uso de janelas com ordenação global para geração de surrogate keys:

```text
Window.orderBy(...)
row_number()
```

Esse processo exigia ordenação de milhões de registros e causava alto consumo de memória.

Para resolver o problema, a geração das chaves substitutas foi alterada para uma estratégia baseada em hash determinístico com `xxhash64`.

Essa alteração reduziu o uso de memória e eliminou a necessidade de ordenação global para geração das chaves.

As chaves das dimensões foram alteradas para o tipo `BIGINT` no MySQL para suportar os valores gerados por hash.

---

## 11. Banco de Dados

O banco utilizado no projeto é:

```text
enem_dw
```

As tabelas criadas são:

```text
dim_candidato
dim_escola
dim_local_prova
dim_socioeconomica
fato_resultados
```

O script de criação das tabelas está localizado em:

```text
sql/create_tables.sql
```

Para criar ou recriar as tabelas:

```powershell
Get-Content .\sql\create_tables.sql | docker exec -i enem_mysql mysql -uroot -proot enem_dw
```

---

## 12. Execução do Projeto

### 12.1 Subir o container MySQL

```powershell
docker compose up -d
```

### 12.2 Ativar o ambiente virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 12.3 Configurar o Hadoop no PowerShell

```powershell
$env:HADOOP_HOME="C:/hadoop"
$env:PATH="C:/hadoop/bin;$env:PATH"
```

### 12.4 Criar as tabelas

```powershell
Get-Content .\sql\create_tables.sql | docker exec -i enem_mysql mysql -uroot -proot enem_dw
```

### 12.5 Executar o ETL

```powershell
python etl/main.py
```

---

## 13. Validação da Carga

Após a execução do ETL, a carga pode ser validada com a seguinte consulta:

```powershell
docker exec -it enem_mysql mysql -uroot -proot -e "USE enem_dw; SELECT 'dim_candidato' AS tabela, COUNT(*) AS total FROM dim_candidato UNION ALL SELECT 'dim_escola', COUNT(*) FROM dim_escola UNION ALL SELECT 'dim_local_prova', COUNT(*) FROM dim_local_prova UNION ALL SELECT 'dim_socioeconomica', COUNT(*) FROM dim_socioeconomica UNION ALL SELECT 'fato_resultados', COUNT(*) FROM fato_resultados;"
```

O principal ponto de validação é garantir que a tabela `fato_resultados` tenha sido carregada corretamente e possua volume compatível com o total de candidatos processados.

---

## 14. Indicadores SQL

Os indicadores foram organizados no arquivo:

```text
sql/indicadores.sql
```

As perguntas respondidas por SQL incluem:

1. Grupo escolar com maior média de notas
2. Aluno com maior média de notas e respectiva média
3. Média geral
4. Percentual de ausentes
5. Número total de inscritos
6. Média por disciplina
7. Média por sexo
8. Média por etnia/cor-raça
9. Média por faixa etária
10. Média por dependência administrativa da escola

Para executar os indicadores:

```powershell
Get-Content .\sql\indicadores.sql | docker exec -i enem_mysql mysql -uroot -proot --table enem_dw
```

Para salvar os resultados em arquivo:

```powershell
Get-Content .\sql\indicadores.sql | docker exec -i enem_mysql mysql -uroot -proot --table enem_dw | Out-File -Encoding utf8 resultados_indicadores.txt
```

---

## 15. Status Atual do Projeto

Até o momento, foram concluídas as seguintes etapas:

* Estruturação do projeto
* Configuração do ambiente Python
* Configuração do Docker com MySQL
* Criação do banco `enem_dw`
* Criação das tabelas dimensionais e da tabela fato
* Implementação da extração da base CSV
* Implementação das transformações com PySpark
* Implementação da carga via JDBC para MySQL
* Criação do modelo dimensional
* Criação das consultas SQL de indicadores
* Ajuste de performance para evitar erro de memória no Spark
* Adequação das chaves substitutas para `BIGINT`
* Documentação técnica parcial do projeto

Etapas ainda pendentes:

* Finalizar e validar a carga completa da base
* Executar os indicadores finais com a base completa
* Gerar arquivos agregados para visualização
* Criar gráficos analíticos
* Construir dashboard
* Elaborar conclusões e insights finais
* Finalizar documentação com resultados obtidos
* Subir versão final no GitHub

---

## 16. Próximas Etapas

As próximas etapas planejadas são:

1. Validar a carga completa no MySQL
2. Executar o arquivo `indicadores.sql`
3. Salvar os resultados finais dos indicadores
4. Criar bases agregadas para análise visual
5. Construir visualizações gráficas
6. Criar dashboard final
7. Documentar os insights obtidos
8. Finalizar o repositório para entrega

---

## 17. Considerações Finais

O projeto foi estruturado para demonstrar um fluxo completo de dados, partindo da base bruta dos Microdados do ENEM 2020 até um modelo dimensional em banco MySQL.

A utilização de PySpark permite processar uma base de grande volume, enquanto o MySQL em Docker facilita a reprodução do ambiente. A modelagem dimensional favorece a análise dos dados por diferentes perspectivas, como perfil do candidato, escola, local de prova e características socioeconômicas.

A documentação será atualizada após a conclusão da carga completa, execução dos indicadores finais, criação das visualizações e desenvolvimento do dashboard.
 
