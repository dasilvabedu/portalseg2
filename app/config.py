# Conexão ao Postgres
# conecta ao servidor PostgreSQL - Google cloud
# DATABASE_PROD_URL = "postgres://portalseg:WAgqyA7GDmeL22gXiskJAWZpzRMiaiEyHHKsofLVjwaCGWboJ7vbpqHHjpAbjYRe@portal.geocart.xyz:5432/portalseg"
# conecta ao novo servidor Local
# DATABASE_PROD_URL = "postgres://postgres:ProjetoCTG@localhost:5432/midiasii"
# conecta ao servidor PostgreSQL - Heroku
# DATABASE_PROD_URL = "postgres://ecslunsebgmwsg:e223d30d113882a52c5bb00b34b79e647ca906f542ea9df492226725a970d9a5@ec2-52-200-119-0.compute-1.amazonaws.com:5432/db7v0ile7h9t4v"
# conecta ao servidor PostgreSQL - Heroku NOVO
# DATABASE_PROD_URL = "postgres://sjnbgfuswdvxns:ce2693a165ae39084f9d27a064a32f3c54063f8cac841d6ea3320fd9838639c1@ec2-184-73-249-9.compute-1.amazonaws.com:5432/d7iuipfha637p9"

# conecta ao servidor Amazon
DATABASE_PROD_URL = (
    "postgres://postgres:fSFC9LVnd2GBQZVG@rapidpro.c9aatnzr39zi.us-east-1.rds.amazonaws.com/portalseg?sslmode=disable"
)


# Secret Key
SECRET_KEY = b"i\xfc\xc9\x04\x93d\xaaW\xd7D\x87JLd!\xbd)\xbc\xa5\xc5\xc6 \x05\xf0\xc7t\x14\xbc\x82\xdb\x98\n"

# Tempo em minutos para validade do Token
DURACAO_TOKEN = 240

# Parâmetros para acesso ao envio de mensagens
CAMINHO_MENSAGEM = "https://capacitacao.geocart.xyz/api/v2/flow_starts.json"
HEADER_MENSAGEM = "Token ce5ed3234011bc9b936a80851141869f347191d2"
FLOW_MENSAGEM = "27fa4531-ca61-4b55-8238-03948d286bdf"
