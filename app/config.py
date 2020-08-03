# Conexão ao Postgres
# conecta ao servidor PostgreSQL - Google cloud
#DATABASE_PROD_URL = "postgres://portalseg:WAgqyA7GDmeL22gXiskJAWZpzRMiaiEyHHKsofLVjwaCGWboJ7vbpqHHjpAbjYRe@portal.geocart.xyz:5432/portalseg"
# conecta ao novo servidor Local
DATABASE_PROD_URL = "postgres://postgres:ProjetoCTG@localhost:5432/midiasii"
# conecta ao servidor PostgreSQL - Heroku
# DATABASE_PROD_URL = os.environ['DATABASE_URL']

# Secret Key
SECRET_KEY = b'i\xfc\xc9\x04\x93d\xaaW\xd7D\x87JLd!\xbd)\xbc\xa5\xc5\xc6 \x05\xf0\xc7t\x14\xbc\x82\xdb\x98\n'

# Tempo em minutos para vaidade do Token
DURACAO_TOKEN = 60

