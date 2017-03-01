Чтобы запустить докер:

        docker build -t webchat .

        docker run -ti -p 8000:8000 -v `pwd`/:/webchat webchat /webchat/entrypoint.sh
