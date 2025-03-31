# Ativa
Interface para facilitar a vida do TI na Ativa Locação

# Passos
1. Criar repositório "ativa" no Github com README, LICENSE e .gitignore para Python

2. Instalar Nginx e CertBot:
```
apt install nginx certbot python3-certbot-nginx
```

4. Instalar e configurar um firewall permitindo apenas SSH, HTTP e HTTPS:
```
apt install ufw
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

4. Criar certificado Let's Encrypt com certbot para o domínio que vai usar, aqui no caso será polegato.ddns.net (criado no noip.com para DDNS)
   - 4.1. Deve-se apontar no DNS para o IP público da rede do servidor com Nginx
   - 4.2. Caso tenha roteador e/ou firewall na rede do IP público, deve-se liberar e direcionar as portas 80 e 443 para Nginx do IP internet do servidor
   - 4.3. Solicitar o certificado e configurar o site Nginx padrão:
   ```
   certbot --nginx -d polegato.ddns.net
   ```
   - 4.4. Acessar http://polegato.ddns.net e verificar se carregou a página do Nginx com HTTPS e certificado correto.

5. Criar o diretório /var/www/ativa_root e entrar nele:
```
mkdir /var/www/ativa_root
cd /var/www/ativa_root
```

6. Criar virtualenv e ativar:
```
apt install virtualenv
virtualenv .env && . .env/bin/activate
```

7. Instalar o Django e Gunicorn:
```
pip install django django-compressor gunicorn
```

8. Clonar, com a devida chave SSH, este repositório do Github (ex.: <chave_ssh_do_github>=/home/junior/.ssh/id_rsa e <usuário_github>=JuniorPolegato):
```
ssh-agent bash -c "ssh-add <chave_ssh_do_github>; git clone git@github.com:<usuário_github>/ativa.git ativa.git"
```

9. Entrar no diretório no repositório e inciar o projeto Django, entrando no diretório do projeto:
```
cd ativa.git
django-admin startproject ativa
cd ativa
```

10. Configurar o serviço do Gunicorn na estrutura systemd para o usuário www-data:
```
mkdir /run/gunicorn

cat << EOF > /etc/systemd/system/gunicorn.socket
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn/ativa.sock

[Install]
WantedBy=sockets.target
EOF

cat << EOF > /etc/systemd/system/gunicorn.service
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ativa_root/ativa.git/ativa
ExecStart=/var/www/ativa_root/.env/bin/gunicorn \\
          --access-logfile - \\
          --workers 3 \\
          --bind unix:/run/gunicorn/ativa.sock \\
          ativa.wsgi:application

[Install]
WantedBy=multi-user.target
EOF
```

11. Ativar e monitorar o serviço:
```
journalctl --follow -u nginx.service &
journalctl --follow -u gunicorn.service &
journalctl --follow -u gunicorn.socket &
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
```

12. Configurar no Ngnix um proxy reverso para este socket do Gunicorn:
```
sed -i '/^\s*location\s*\/\s*{.*/{:a; n; /^\s*location\s*\/\s*{.*/! ba; :b; s/.*//; N; /^\s*}/! bb; s/.*/\tlocation = \/favicon.ico {\n\t\taccess_log off;\n\t\tlog_not_found off;\n\t}\n\n\tlocation \/static\/ {\n\t\troot \/var\/www\/ativa_root;\n\t}\n\n\tlocation \/ {\n\t\tinclude proxy_params;\n\t\tproxy_pass http:\/\/unix:\/run\/gunicorn\/ativa.sock;\n\t}/}' /etc/nginx/sites-available/default
nginx -t
systemctl restart nginx.service
```

13. Autorizar o Django para o domínio polegato.ddns.net, parar o serviço do Gunicorn e depois acessar o site https://polegato.ddns.net:
```
sed -i 's/^\(ALLOWED_HOSTS\s*=\s*\).*/\1\["localhost", "polegato.ddns.net"\]/' ativa/settings.py
systemctl stop gunicorn.service
```
Neste ponto deve estar rodando 100% com a página inicial do Django.
Nessta variável `ALLOWED_HOSTS` no arquivo `ativa/settings.py` pode-se adicionar outros sites que poderão rodar esta aplicação em Django.

14. Criar o usuário super, digitar e-mail e senha quando perguntado, e finalizar ajustes iniciais nas configurações:
```
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser
sed -i "/^INSTALLED_APPS\s*/{:a; n; /\s*\]/! ba; s/\(.*\)\(\].*\)/\1\1    'compressor',\n\1\2/}" ativa/settings.py
sed -i "s/^STATIC_URL\s*.*/STATIC_URL = 'static\/'\nSTATIC_ROOT = '\/var\/www\/ativa_root\/static\/'/" ativa/settings.py
sed -i "s/^LANGUAGE_CODE\s*.*/LANGUAGE_CODE = 'pt-br'/" ativa/settings.py
sed -i "s/^TIME_ZONE\s*.*/TIME_ZONE = 'America\/Sao_Paulo'/" ativa/settings.py
echo -e "\nCOMPRESS_URL = STATIC_URL\nCOMPRESS_ROOT = STATIC_ROOT\nCOMPRESS_STORAGE = 'staticfiles.storage.StaticFileStorage'" >> ativa/settings.py
./manage.py collectstatic
systemctl stop gunicorn.service
chown www-data: . db.sqlite3
```
Agora acessar https://polegato.ddns.net/admin e verificar se esta etapa de instalação do Django está terminado.

15. Com tudo certo, fazer um commit com Django instalado:
```
pip freeze > requirements.txt
git add .
git commit -m "Django instalado"
ssh-agent bash -c "ssh-add <chave_ssh_do_github>; git push"
```

16. Para cada novo `git clone` ou `git pull`, é importante instalar pacotes do Python necessários:
```
pip install -r requirements.txt
```

17. Para desenvolvimento e teste local, utilize os passos 6, 7 e 8 para clonar, entrar no diretório clonado, executar as três primeiras linhas do passo 14, depois somente utilizar `git pull` para puxar atualizações, `git add .` para adicionar novidades, `git commit -m "<mensagem>"` para agrupar as novidades e colocar uma mensagem neste grupo, e por fim `git push` para enviar alterações. Sendo que para executar o Django locamento utilize:
```
./manage.py runserver localhost:8000
```
E para acessar utilize http://localhost:8000, que deverá também aparece na tela após o comando acima

18. Criação do home para login e as funções básicas de autenticação no Totvs/Protheus e uso do respecitivo banco de dado MS SQL Server
  - adiconado "metabaseativa.ddns.net" em `ALLOWED_HOSTS` no arquivo `ativa/settings.py` para levantar um novo servidor na AWS posteriormente
  - `./manage.py startapp home`
  - adicionado "home" em `INSTALLED_APPS` no arquivo `ativa/settings.py`
  - criada a tabela `ReleaseBilling` no arquivo `home/models.py`
  - registrada a tabela para aparecer no sistema administrativo do Djando no arquivo `home/admin.py`
  - criado o diretório `home/db` para conexão e funcionalidades para com o banco de dados
  - criado o diretório `home/totvs_api` para utlização das APIs do Totvs/Protheus, inicialmente autenticação
  - criado os diretórios para templates e arquivos estáticos: `home/templates` e  `home/static`
  - criado o arquivo com as funcões a serem utilizadas para renderizar telas e operações em `home/views.py`
  - criado as rotas para trabalho dentro de home em `home/urls.py` chamando as funções em `home/views.py`
  - criada a rota inicial apontando para o app home em `ativa/urls.py`
  - lembrar de conectar a VPN pra ter acesso aos servidores do Protheus e Banco de Dados
  - para utlizar o banco de dados MS SQL Server, deve-se instalar os pacotes necessários para o sistema operacional (Debian GNU/Linux neste caso):
  ```
  sudo curl https://packages.microsoft.com/config/debian/12/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
  sudo curl https://packages.microsoft.com/keys/microsoft.asc  | sudo gpg --dearmor --output /usr/share/keyrings/microsoft-prod.gpg
  sudo apt update
  sudo ACCEPT_EULA=Y apt install msodbcsql18 mssql-tools18
  echo -e '\nexport PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
  . ~/.bashrc
  ```
  - Por fim os pacotes do Python necessários para rodar estas funcionalidades implementadas
  ```
  pip install requests
  pip install lxml
  pip install pyodbc
  pip freeze > requirements.txt
  ```
  - Agora a etapa de aplicar as alterções no banco de dados, coletar os arquivos estáticos para Nginx e, estando tudo certo, rodar o teste:
  ```
  ./manage.py makemigrations
  ./manage.py migrate
  ./manage.py collectstatic
  ./manage.py runserver localhost:8000
  ```
  - Após testado, o commit e push conforme passo 15

19. No servidor de teste, o deploy do home:
  - Se for necessário, deve-se instalar pacotes no sistema que não são parte do Python, mas necessário para o funcionar, MS SQL Server Driver neste caso:
  ```
  sudo curl https://packages.microsoft.com/config/debian/12/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
  sudo curl https://packages.microsoft.com/keys/microsoft.asc  | sudo gpg --dearmor --output /usr/share/keyrings/microsoft-prod.gpg
  sudo ACCEPT_EULA=Y apt install msodbcsql18 mssql-tools18
  echo -e '\nexport PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
  . ~/.bashrc
  ```
  - Agora sim os comandos que devem rodar a cada deploy:
  ```
  cd /var/www/ativa_root/ativa.git/ativa
  . ../../.env/bin/activate  # se não já estiver no ambiente virtual (virtualenv)
  systemctl stop gunicorn.socket gunicorn.service
  ssh-agent bash -c "ssh-add <chave_ssh_do_github>; git pull"
  pip install -r requirements.txt
  ./manage.py makemigrations
  ./manage.py migrate
  ./manage.py collectstatic
  chown www-data: . db.sqlite3 home/totvs_api/acessos_totvs.json
  systemctl start gunicorn.socket
  ```
  - Após isto, acessar o site público https://polegato.ddns.net

20. Novo servidor em https://metabaseativa.ddns.net:15443
  - Neste caso já tem instalado e funcionando o Nginx para outro serviço neste domínio, já com certificado de criptografia, pularemos os passos 1, 2 e 4.
  - Liberar porta 15443 conforme passo 3.
  - Seguir os passos 5 e 6, pular o 7, criando diretório e ambiente para comportar o aplicativo.
  - Clonar coforme passo 8, onde uma chave autorizada do repositório no Github deverá estar em algum arquivo com permissão `600` para `<chave_ssh_do_github>`.
  - Pular o passo 9, seguir os passos 10 e 11 para criar e ativar o serviço do Gunicorn.
  - No passo 12, antes copiar a configuração do site `/etc/nginx/sites-available/default` para `/etc/nginx/sites-available/metabaseativa.ddns.net_15443`.
    - Esta configuração copiada precisa estar com o certificado configurado, pois a intenção é utilizar a estrutra deste arquivo, aproveitando as linhas de SSL
    - O comando de adquação do arquivo de configuração do site se aplica a cópia do `default`, caso tenha mudado algo, manualmente excluir os `locations` e outras funcionalides e criar conforme este comando os três `location`s necessários: `/favicon.ico`, `/static/` e `/`.
    - Trocar a porta segura de 443 para 15443, que foi a porta escolhida aqui, então excluir as outras sessões de `server` deste arquivo.
    - O resultado final deverá ser semelhante a este:
    ```
    server {
      root /var/www/html;

      # Add index.php to the list if you are using PHP
      index index.html index.htm index.nginx-debian.html;

      server_name metabaseativa.ddns.net; # managed by Certbot

      location = /favicon.ico {
        access_log off;
        log_not_found off;
      }

      location /static/ {
        root /var/www/ativa_root;
      }

      location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn/ativa.sock;
      }

      listen [::]:15443 ssl ipv6only=on; # managed by Certbot
      listen 15443 ssl; # managed by Certbot
      ssl_certificate /etc/letsencrypt/live/metabaseativa.ddns.net/fullchain.pem; # managed by Certbot
      ssl_certificate_key /etc/letsencrypt/live/metabaseativa.ddns.net/privkey.pem; # managed by Certbot
      include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
      ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    }
    ```
    - Ativar este site e testar se o arquivo de configuração está ok, e recarregar o Nginx se estiver tudo ok:
    ```
    ln -s /etc/nginx/sites-available/metabaseativa.ddns.net_15443 /etc/nginx/sites-enabled/
    nginx -t
    systemctl reload nginx
    ```
  - Neste ponto já se tem o site ar na porta especificada, agora seguir o deploy conforme passo 19.
  - Após isto, acessar o site público https://metabaseativa.ddns.net:15443
  - Neste momento, não se teve ainda o cadastro dos usuários e seus acessos, então deve-se criar um usuário super isso:
  ```
  ./manage.py createsuperuser
  ```
  - Após isto, acessar o site público https://metabaseativa.ddns.net:15443/admin e adcionar em `Authorized users`

21. Melhorado um pouco a visualização do projeto via https://divtable.com/table-styler/.
  - Adotado formato padrão sugerido de tabela azul com CSS, copiar e colcar, depois justar o `for` para as linhas.
  - Adicionados na visualização dados dos campos presentes na tabela SX3(010).
  - Passo 15 para subir as alterações no Github com nova mensagem, ou via IDE, mas não esquecer do `pip freeze > requirements.txt`.
  - Passo 19, segunda parte que diz respeito ao deploy, visto que o driver já foi instalado.

22. Forçar refazer login com usuário e senha e não utilizar o último token, que é útil apenas para usuário de API, com tempo de sessão.
  - Definido 5 minutos (300 segundos) para a sessão e então fazer logout quando tentar alguma operação
  - Mostrar o tempo que ainda tem para expirar quando atualizar a tela


# MSys2 with GCC and Python

Download latest MSys2 from:
```
https://github.com/msys2/msys2-installer/releases/download/nightly-x86_64/msys2-x86_64-latest.exe
```

Run `msys2-x86_64-latest.exe`

On the `UCRT64` terminal, run:
```
pacman -Syu
```
It will be closed if update successful.

Reopen UCRT64 and run:
```
pacman -Su
pacman -S git base-devel mingw-w64-ucrt-x86_64-toolchain mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-unixodbc mingw-w64-ucrt-x86_64-python-setuptools mingw-w64-ucrt-x86_64-python-pip mingw-w64-ucrt-x86_64-python-wheel mingw-w64-ucrt-x86_64-python-pytest mingw-w64-ucrt-x86_64-python-lxml mingw-w64-ucrt-x86_64-python-pillow mingw-w64-ucrt-x86_64-python-pyreadline3
cp -av /ucrt64/lib/libz.a /ucrt64/lib/libzlib.a
cp -av /ucrt64/lib/libz.dll.a /ucrt64/lib/libzlib.dll.a
```

Add into user environment variable `Path`, the values `C:\msys64\ucrt64\bin` and `C:\msys64\usr\bin`

## Virtual environment with `pyodbc`, `lxml` and `pillow`:
```
python -m venv .env
. .env/bin/activate
python -m pip install --upgrade pip
pip install pyreadline
sed -i 's/collections.Callable/collections.abc.Callable/g' .env/lib/python3.12/site-packages/pyreadline/py3k_compat.py

git clone https://github.com/RoDuth/pyodbc.git
tar czvf pyodbc.tar.gz pyodbc
pip install pyodbc.tar.gz
rm -rf pyodbc*

export CFLAGS="-I/ucrt64/include/"
pip install -r ativa/requirements_djlint.txt
```

## Bash terminal into Codium:

```
{
    "files.trimTrailingWhitespace": true,
    "files.autoSave": "afterDelay",
    "editor.renderWhitespace": "all",
    "terminal.integrated.profiles.windows": {
        "UCRT64 Bash": {
            "source": "Bash",
            "path": "C:/msys64/usr/bin/bash.exe",
            "args": [
                "--login",
                "-i"
            ],
            "env": {
                "MSYSTEM": "UCRT64",
                "CHERE_INVOKING": "1",
                "MSYS2_PATH_TYPE": "inherit"
            }
        }
    },
    "terminal.integrated.defaultProfile.windows": "UCRT64 Bash",
    "workbench.editor.enablePreview": false,
    "git.autofetch": true,
    "git.path": "C:\\Program Files\\Git\\cmd\\git.exe",
    "python.createEnvironment.trigger": "off"
}
```
