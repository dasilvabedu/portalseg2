"# portalsegbar2" 

Você deve ter conta no GIT Hub e no Heroku

No prompt de comando, ir para o diretório de seu projeto:

C:\Users\<username>\<seu diretório> $ cd portalsegbar2/
C:\Users\<username>\<seu diretório>\portalsegbar2> $

Registro no GIT:
No GIT HUB criar seu repositório (ex: <seu usuario>/portalsegbar2.git)

No termimal, no seu diretório:

$ git init
$ git add README.md
$ git commit -m"first-commit"
$ git remote add origin https://github.com/<seu user name>/portalsegbar2.git
$ git push -u origin master

Deploy no Heroku:

C:\Users\<username>\<seu diretório>\portalsegbar2> $ heroku login

+++ Instalar as dependências do seu projeto  ++++
exemplo : pip install flask

Criar arquivo com as dependências do projeto (requirements.txt):

C:\Users\<username>\<seu diretório>\portalsegbar2> $ pip freeze > requirements.txt

(importante : deve ser especificidao a extensão ".txt")

Criar o arquivo Procfile :

arquivo texto:

web: gunicorn segurancaBarragem:app

Salvar como Procfile (sem extensão)

Utilizar os comandos:

C:\Users\<username>\<seu diretório>\portalsegbar2> $ git add .
C:\Users\<username>\<seu diretório>\portalsegbar2> $ git commit -m"heroku deploy"
C:\Users\<username>\<seu diretório>\portalsegbar2> $ git push heroku master
C:\Users\<username>\<seu diretório>\portalsegbar2> $ heroku open

== Neste instante você pode acessar a URL do seu site (https:\\portalsegbar2.herokuapp.com\....

Para rodar localmente:

utilizar ambiente virtual como por exemplo o Pycharm

Para instalar as dependencias do projeto, no terminal do Pycharm,na pasta do projeto, rodar o comando abaixo:

$ pip install requirements.txt

Após concluir a instalação, rodar o comando abaixo para subir o projeto:

- Abrir o arquivo segurancaBarragem.py e na barra de opções selecionar 'Run segurancabarragem"

O seu projeto estará rodando no endereço : http://127.0.0.1:5000/seguranca_barragem/....





