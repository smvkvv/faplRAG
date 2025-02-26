# faplRAG

## Проект и его бизнес-ценность

RAG-система для новостей с сайта английской Премьер-лиги по футболу. Основной упор при разработке был направлен на инжиниринг управления данными, например, на создание регулярного процесса по парсингу данных с сайта в Apache Airflow 

В эпоху бума популярности AI-ассистентов актуальность проекта не вызывает сомнений, он может быть использован для новых B2C или B2B продуктов, таких как:

* Персонализированные футбольные ассистенты для болельщиков.
* Инструменты для спортивных аналитиков и журналистов.
* Платформы для управления спортивным контентом.

Личное увлечение футболом также послужило одной из причин для выбора данного проекта.

## Детали разработки проекта

### Сбор и предобработка данных

Сбор данных осуществляется парсингом новостей с сайта fapl.ru с помощью beautifulSoup4. Исходный код находится в utils/parser.py

1. Сначала парсится url со списком опубликованных новостей за определенный месяц: http://fapl.ru/calendar/2024/12/, на выходе получаем список url для парсинга
2. Для каждой url запускаем процесс парсинга контента страницы, его предобработки и обертку в класс `Post(pydantic.BaseModel)`
3. Также текст новости каждого поста векторизуется для будущего складывания в векторную БД.

P.S. Здесь какой-то серьезной валидации данных не было сделано, так получилось, что новости с сайта оказались все полноформатными без пропусков и ошибок.

### Исследовательский анализ данных. Метрики качества

В тетрадке experiments/eda.ipynb можно найти EDA для 4-х месяцев данных, около 2 тысяч новостей. Основной упор анализа направлен на выявление полезных инсайтов из данных относительно задачи RAG.

По метрикам качества, к сожалению, не получилось явно придумать те, которые было бы полезно отслеживать. Опять же, "хорошесть" данных в кейсе с заполненными без ошибок новостями нужно было определять как что-то комплексное (сложное). Возможно, если бы не потратил слишком много времени на поднятие Airflow, успел бы разобраться :(

### Разработка базы данных для хранения данных

Здесь получилось относительно неплохо, удалось поднять две БД:

1. PostgreSQL с плагином pgvector для векторного поиска. Хотелось в целом иметь векторную БД, был выбор между Qdrant, Milvus, PostgreSQL. Так как опыт с постгрей уже был, остановился на ней.


2. OpenSearch как NoSQL полнотекстовая БД. Здесь тоже чуть пришлось пободаться, сначала взял ElasticSearch, пытался поднять его, но из-за санкций к пользователям из России, без впна что-то нормально не заводилось. 
По итогу нашел альтернативу в виде OpenSearch.

   
### Автоматизация пайплайна

Часть проекта, на которую было потрачено больше всего времени, так как решил, что смогу справиться с Airflow. В итоге справился, но через боли и мучения.

Есть DAG в Airflow, который парсит данные, обрабатывает их и складывает в БД. Здесь по мониторингу максимум - принт каких-то логов, дашбордов нет.
Но хочется отметить, что когда я это доделал, в дальнейшем было очень удобно разрабатывать остальную часть проекта, так как просто делал make setup, запускал DAG и 
в двух БД по итогам выполнения лежали данные.

p.s. проблемы возникали, например, с определение pythonpath внутри контейнера, даже когда явно указывался в коде, не подтягивались модули из других папок, решил хардкодом...

### Дашборд

Здесь, к сожалению, как и с метриками качества не получилось придумать, что именно отражать на дашборде. Наверняка при более глубоком анализе это бы получилось, но не хватило времени :(

