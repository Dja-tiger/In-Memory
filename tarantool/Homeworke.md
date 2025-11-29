Нагрузочное тестирование выполняется скриптом dialog_benchmark.py, который генерирует нагрузку на обе реализации хранилища (SQLiteDialogStore и TarantoolDialogStore) по одному и тому же сценарию:

массовая вставка сообщений в диалог (add_message),

чтение диалогов (get_dialog),

измерение QPS и p50 latency.

Запуск бенчмарка автоматизирован в скрипте:

cd tarantool
./run_dialogs.sh


Результаты теста:

SQLiteDialogStore        write_qps=279875.2 read_qps= 42141.5 p50=0.001ms
TarantoolDialogStore     write_qps=  2503.3 read_qps=  1850.5 p50=0.381ms

Migration speed-up (writes): ×0.01


Таким образом, проведено сравнение производительности модуля «до» (SQLite) и «после» переноса логики в In-Memory СУБД (Tarantool + UDF), что удовлетворяет требованию по нагрузочному тестированию и сравнительному анализу.

Описание запуска в tarantool/README.md