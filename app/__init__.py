from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

from .models import gestaoDado, gestaoMetadado, gestaoUsuario, gestaoOrganizacao
from .models import gestaoAutenticacao, gestaoDocumentacao, gestaoChatterbot, gestaoUHE
from .models import gestaoAgente, gestaoMorador, gestaoPerfil, gestaoCapacitacao
from .views import acessoBanco
from .controllers import rotaDado, rotaErro, rotaMetadado, rotaUsuario, rotaOrganizacao
from .controllers import rotaAutenticacao, rotaDocumentacao, rotaChatterbot, rotaUHE
from .controllers import rotaAgente, rotaMorador, rotaPerfil, rotaCapacitacao
