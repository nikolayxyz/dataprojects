Для корректной работы установите библиотеки используя файл requirements.txt.
Создайте базу данных zen командой pg_restore -d zen zen.dumps.
Сначала запустите пайплайн командой python3 zen_pipeline.py
Затем запустите дешборд: python3 zen_dashboard.py
Для обновления в кроне пропишите следующую комманду(crontab -e): * 23 * * * python3 zen_pipeline.py
