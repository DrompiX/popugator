### Процесс миграции для изменения
> Во время работы с таск трекером, мы поняли, что попуги часто в title задачи пишут
конструкцию [jira-id] - Title (Пример: "UBERPOP-42 — Поменять оттенок зелёного на кнопке").
В результате чего поэтому нам необходимо разделить title на два
поля: title (string) + jira_id (string). При этом, для всех новых событий, необходимо
убедиться что jira-id не присутствует в title. Для этого достаточно сделать валидацию
на наличие квадратных скобок (] или [)

### Что нужно сделать
- Изменить модель данных для `Task`
- Изменить модель данных для создания задачи в API, добавить
валидацию на отсутствие `[` и поправить код в API Task Manager
- Мигрировать схемы в БД всех сервисов
- Поправить модель событий по задачам, включить в нужные `jira_id`
- Создать новые версию схем для `TaskAdded` и `TaskCreated`
- Поправить обработку измененных событий в каждом заинтересованном сервисе,
перевести их на новую схему