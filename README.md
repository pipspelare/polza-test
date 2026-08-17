## Запуск 

docker compose up -d --build

pip install -r requirements.txt

python3 load_data.py

##### *запросы из первого задания ⬇️
docker compose exec -T postgres psql -U app -d companies  < queries.sql

cd web

npm install

##### *в prod'e так не буду делать :) ⬇️
cat .env.example > .env.local 

npm run dev

## Задача 2

Запустил PostgreSQL через docker compose up -d, затем запустил Next.js командой npm run dev и открыл страницу /companies. Проверил, что таблица компаний загружается из базы, поиск по названию меняет URL и отфильтровывает список, а выбор города оставляет только компании из выбранного города. Также проверил комбинацию поиска и фильтра, сброс фильтров и пустой результат по несуществующему названию. В процессе сборка сначала ломалась из-за глобальных селекторов table и td a в CSS Module, поэтому добавил локальные классы .table и .siteLink, после чего страница успешно запустилась.

![Alt text](/screenshots/20-22-50.png)
![Alt text](/screenshots/20-22-58.png)
![Alt text](/screenshots/20-23-29.png)
![Alt text](/screenshots/20-23-16.png)
